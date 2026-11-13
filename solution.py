import pandas as pd
import ast
import re

# only letters or underscore
COLUMN_NAME_PATTERN = r"^[a-zA-Z_]+$"

def add_virtual_column(df: pd.DataFrame, role: str, new_column: str) -> pd.DataFrame:
    try:
        tree = ast.parse(role.strip(), mode='eval')
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        if not isinstance(new_column, str):
            return pd.DataFrame([])

        if re.fullmatch(COLUMN_NAME_PATTERN, new_column) is None:
            print(f"Invalid new_column name: {new_column}. It should only contain letters or underscores.")
            return pd.DataFrame([])

        for column in df.columns:
            if not isinstance(column, str):
                return pd.DataFrame([])
            if re.fullmatch(COLUMN_NAME_PATTERN, column) is None:
                print(f"Invalid column name: {column}. It should only contain letters or underscores.")
                return pd.DataFrame([])

        if not names.issubset(df.columns):
            print(f"Invalid role: {role}. It contains column names that are not in the DataFrame.")
            return pd.DataFrame([])

        result = df.copy()
        result[new_column] = df.eval(role)
        return result
    except (SyntaxError, ValueError, KeyError, TypeError, ArithmeticError):
        print(f"Invalid role: {role}. It should be a valid arithmetic expression using existing column names.")
        return pd.DataFrame([])