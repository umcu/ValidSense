import pandas as pd


def df_rename_col(df: pd.DataFrame, column_name_old: str, column_name_new: str):

    """
    Function to rename column name in dataframe from column_name_old to column_name_new.
    :param df: (pandas DataFrame) dataframe.
    :param column_name_old: (str) old column name.
    :param column_name_new: (str) new column name.
    :return: (pandas DataFrame) dataframe with changed column name.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pd.DataFrame")
    if not isinstance(column_name_old, str):
        raise TypeError(f"column_name_old is of type {type(column_name_old).__name__}, should be str")
    if not isinstance(column_name_new, str):
        raise TypeError(f"column_name_new is of type {type(column_name_new).__name__}, should be str")
    if column_name_old not in df.columns:
        raise KeyError("column_name_old not existing in df.")

    try:
        df.rename(columns={column_name_old: column_name_new}, inplace=True)
        return df

    except Exception as e:
        return e
