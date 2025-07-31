import teradataml as tdml
import pandas as pd
import networkx as nx
from ._dataframe_lineage_utils import (analyze_sql_query, query_replace, query_change_case)
from collections import OrderedDict
from typing import Optional, Union, List

def corr(self, method: str = 'pearson') -> tdml.DataFrame:
    """
    Compute the correlation matrix of the DataFrame using VAL.

    Currently, only Pearson correlation is supported. Requires
    `val_install_location` to be set in `tdml.configure`.

    Args:
        method (str, optional): Correlation method. Must be 'pearson'.

    Returns:
        tdml.DataFrame: A DataFrame containing the correlation matrix.
    """
    assert method == "pearson", "only pearson is currently supported"
    assert tdml.configure.val_install_location not in ["", None], \
        "set val install location, e.g. `tdml.configure.val_install_location = 'val'`"

    DF_corrmatrix = tdml.valib.Matrix(
        data=self,
        columns=list(self.columns),
        type="COR"
    ).result

    return DF_corrmatrix



def show_CTE_query(self) -> str:
    """
    Generate a single CTE (Common Table Expression) SQL query
    representing the lineage of a teradataml DataFrame.

    Consolidates all intermediate transformations
    into a single SQL statement for deployment.

    Returns:
        str: Full SQL query with all transformations inlined as CTEs.
    """
    tddf = self
    view_name = "pipeline"
    tddf_columns = tddf.columns

    tddf._DataFrame__execute_node_and_set_table_name(tddf._nodeid, tddf._metaexpr)

    tddf_graph_, _ = analyze_sql_query(tddf.show_query(), target=tddf._table_name)

    tddf_graph = pd.DataFrame(
        [(s, t) for s, t in zip(tddf_graph_['source'], tddf_graph_['target']) if s != t],
        columns=['source', 'target']
    )

    dependency_graph = nx.DiGraph()
    dependency_graph.add_edges_from(zip(tddf_graph['source'], tddf_graph['target']))
    sorted_nodes = list(nx.topological_sort(dependency_graph))

    targets = []
    for x in sorted_nodes:
        parts = x.split('.')
        if len(parts) > 1 and (parts[1].upper().startswith('ML__') or parts[1].upper().startswith('"ML__')):
            targets.append(x)

    if len(targets) > 1:
        mapping = OrderedDict({n: f"{view_name}_step_{i}" for i, n in enumerate(targets)})
    elif len(targets) == 1:
        mapping = {tddf_graph['target'].values[0]: view_name}
    else:
        mapping = {tddf._table_name: view_name}

    all_queries = []
    for old_name, new_name in mapping.items():
        raw_query = tdml.execute_sql(f"SHOW VIEW {old_name}").fetchall()[0][0].replace('\r', '\n')
        query = query_change_case(raw_query, 'lower')
        query = query_replace(query, ' create view ', '')
        for old_sub, new_sub in mapping.items():
            query = query_change_case(query, 'upper').replace(old_sub.upper(), new_sub.upper())
        query = query.replace(" AS ", " AS (\n", 1) + "\n)"
        all_queries.append(query)

    combined_ctes = "\n\n,".join(all_queries)
    final_query = f"WITH {combined_ctes}\n\nSELECT * FROM {new_name}"
    return final_query


def deploy_CTE_view(
    self,
    view_name: str,
    schema_name: str = None,
    return_view_df: bool = False
) -> Optional[tdml.DataFrame]:
    """
    Deploy the DataFrame as a SQL view by materializing all transformations
    into a single CTE-based view.

    Args:
        view_name (str): Name of the resulting view.
        schema_name (str, optional): Schema to place the view in.
        return_view_df (bool, optional): If True, return a DataFrame backed by the created view.

    Returns:
        Optional[tdml.DataFrame]: A new DataFrame referencing the view if return_view_df is True, else None.
    """
    assert view_name is not None
    my_CTE_query = self.show_CTE_query()
    full_obj_name = f"{schema_name}.{view_name}" if schema_name else view_name

    tdml.execute_sql(f"CREATE VIEW {full_obj_name} AS {my_CTE_query}")

    if return_view_df:
        return tdml.DataFrame.from_query(f"SELECT * FROM {full_obj_name}")

def easyjoin(
    self,
    other: tdml.DataFrame,
    on: Union[str, List[str]] = None,
    how: str = 'left',
    lsuffix: Optional[str] = None,
    rsuffix: Optional[str] = None
) -> tdml.DataFrame:
    """
    Perform a simplified join on identical column names with optional suffixes.

    This is a convenience wrapper around the standard join, assuming identity
    join columns and optional suffixes. One of lsuffix or rsuffix must remain None
    to identify which side's duplicate columns to drop post-join.

    Args:
        other (tdml.DataFrame): The other DataFrame to join with.
        on (str or List[str]): Column(s) to join on.
        how (str, optional): Type of join - 'left', 'right', 'inner', etc. Default is 'left'.
        lsuffix (str, optional): Suffix to apply to overlapping columns from the left DataFrame.
        rsuffix (str, optional): Suffix to apply to overlapping columns from the right DataFrame.

    Returns:
        tdml.DataFrame: The result of the join with duplicate join columns dropped.
    """
    assert isinstance(on, (str, list)), "`on` must be str or list of str"
    assert any(x is None for x in [lsuffix, rsuffix]), "Only one suffix should be set"

    drop_suffix = ""
    if all(x is None for x in [lsuffix, rsuffix]):
        if how == "right":
            lsuffix = "lt"
            drop_suffix = lsuffix
        else:
            rsuffix = "rt"
            drop_suffix = rsuffix

    join_cols = [on] if isinstance(on, str) else on
    columns_to_be_dropped = [f"{c}_{drop_suffix}" for c in join_cols]

    DF_result = self.join(other, on, how, lsuffix=lsuffix, rsuffix=rsuffix
                         ).drop(columns=columns_to_be_dropped)

    return DF_result

