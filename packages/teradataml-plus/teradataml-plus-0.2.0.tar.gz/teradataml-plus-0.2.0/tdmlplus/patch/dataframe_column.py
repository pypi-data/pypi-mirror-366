from sqlalchemy import func
import re
from typing import Optional, Union, Tuple
from teradatasqlalchemy import INTEGER as tdml_INTEGER
from sqlalchemy import literal_column
from .. import tdml
from sklearn.preprocessing import PowerTransformer
import numpy as np


def trycast(self, type_= None) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Apply a TRYCAST expression to the DataFrame column using the given type.

    This function parses a Python type expression (e.g., teradataml types like
    Integer(), Decimal(precision=6, scale=4)) and constructs the equivalent
    SQL TRYCAST operation to apply to the column.

    Args:
        type_ (Any): A teradataml type object to cast the column to.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new DataFrame Column with the TRYCAST expression applied.
    """
    typestr = type_.__repr__()
    match = re.match(r'(\w+)\((.*?)\)', typestr)
    if match:
        typename, params = match.groups()
        params = params.strip()
        if params:
            values = [v.strip() for v in re.findall(r'=\s*([^,]+)', params)]
            typestr = f"{typename}({', '.join(values)})"
        else:
            typestr = typename
    else:
        typestr = typestr

    new_expression = f"TRYCAST({self.name} AS {typestr})"
    return type(self)(new_expression, type=type_)

def hashbin(
    self,
    num_buckets: int = 100,
    salt: Optional[str] = None
) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Compute a hash bin value for the column expression, optionally salted.

    Args:
        num_buckets (int): Number of buckets to hash into.
        salt (str, optional): Salt to append to the input before hashing.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new expression representing the hash bin.
    """
    if not salt:
        hash_input = self.expression
    else:
        hash_input = func.CONCAT(self.expression, salt)

    new_expression = func.ABS(
        func.FROM_BYTES(
            func.HASHROW(hash_input), "base10"
        ).cast(type_=tdml_INTEGER)
    ) % num_buckets

    return type(self)(new_expression, type=tdml_INTEGER())




def _power_transform_get_lambda(
    self,
    method: str = 'yeo-johnson'
) -> Tuple[str, float]:
    """
    Estimate the lambda parameter for a power transform (Yeo-Johnson or Box-Cox)
    using a sample of data from the column.

    Args:
        method (str, optional): The power transform method. Must be either
            'yeo-johnson' or 'box-cox'. Default is 'yeo-johnson'.

    Returns:
        Tuple[str, float]: The method name and the estimated lambda value.
    """

    assert method in ['yeo-johnson', 'box-cox'], "method must be 'yeo-johnson' or 'box-cox'"

    # Get table, schema, and column information
    table = self.table
    column_name = self.name
    schema_expr = f"{table.schema}." if table.schema is not None else ""

    # Sample up to 10,000 rows to estimate lambda
    res = tdml.execute_sql(
        f"SELECT {column_name} FROM {schema_expr}{table.name} SAMPLE 10000"
    ).fetchall()
    res = np.array(res)

    # Calculate lambda using sklearn's PowerTransformer
    pt = PowerTransformer(method=method, standardize=False)
    if method == "box-cox":
        res = res[res > 0].reshape(-1, 1)
    pt.fit(res)

    def _truncate_float(x):
        RESOLUTION = 6
        return float(format(x, f'.{RESOLUTION}e'))

    pt_lambda = _truncate_float(pt.lambdas_[0])

    return method, pt_lambda



def power_transform(
    self,
    method: str,
    pt_lambda: float
) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Apply a power transformation (Yeo-Johnson or Box-Cox) to the column
    using a pre-estimated lambda value.

    Args:
        method (str): The transformation method, must be 'yeo-johnson' or 'box-cox'.
        pt_lambda (float): The lambda value for the transformation.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new expression representing the transformed column.
    """

    assert method in ['yeo-johnson', 'box-cox'], "method must be 'yeo-johnson' or 'box-cox'"

    colname = self.name

    def power_transform_yeojohnson(colname: str, lambda_: float) -> str:
        if lambda_ == 0:
            lt0 = f"-(POWER(-{colname} + 1, 2 - {lambda_}) - 1) / (2 - {lambda_})"
            gte0 = f"LN({colname} + 1)"
        elif lambda_ == 2:
            lt0 = f"-LN(-{colname} + 1)"
            gte0 = f"(POWER({colname} + 1, {lambda_}) - 1) / {lambda_}"
        else:
            lt0 = f"-(POWER(-{colname} + 1, 2 - {lambda_}) - 1) / (2 - {lambda_})"
            gte0 = f"(POWER({colname} + 1, {lambda_}) - 1) / {lambda_}"
        return f"CASE WHEN {colname} >= 0.0 THEN {gte0} ELSE {lt0} END"

    def power_transform_boxcox(colname: str, lambda_: float) -> str:
        if lambda_ == 0:
            formula = f"LN({colname})"
        else:
            formula = f"(POWER({colname}, {lambda_}) - 1) / {lambda_}"
        return f"CASE WHEN {colname} > 0.0 THEN {formula} ELSE NULL END"

    if method == "yeo-johnson":
        formula = power_transform_yeojohnson(colname, pt_lambda)
    else:
        formula = power_transform_boxcox(colname, pt_lambda)

    new_expression = literal_column(formula, type_=tdml.FLOAT())
    return type(self)(new_expression, type=tdml.FLOAT())


def power_fit_transform(
    self,
    method: str = 'yeo-johnson'
) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Estimate lambda and apply a power transformation (Yeo-Johnson or Box-Cox)
    to the column in a single step.

    Args:
        method (str, optional): The transformation method, must be 'yeo-johnson' or 'box-cox'.
                                Defaults to 'yeo-johnson'.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new expression with the transformation applied.
    """
    _, pt_lambda = self._power_transform_get_lambda(method)
    new_expr = self.power_transform(method, pt_lambda)
    return new_expr
