import pandas as pd
import numpy as np


def missing(df: pd.DataFrame, subset_col: list = None):
    """
    Function to delete rows with missing values (nan), only in the subset of columns. Specific values can also be set
    to nan and can therefore be deleted.
    :param df: (pandas DataFrame) dataframe with missing values.
    :param subset_col: (list, default None) subset of columns of dataframe where rows with missing values are deleted.
    :return: ([pandas Dataframe, pandas Dataframe]) returns dataframes with information about missing values.
    """

    dec_perc = 1    # number of decimals for percentage

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(subset_col, (list, type(None))):
        raise TypeError(f"subset_col is of type {type(subset_col).__name__}, should be list or NoneType")

    try:
        # count total rows
        counts_total = df.shape[0]

        # drop rows with missing values from subsetCol
        df.dropna(axis=0, how='any', inplace=True, subset=subset_col)

        # missing values
        counts_missing = counts_total - df.shape[0]

        subset_n_perc = [
            str(counts_missing) + " (" + str(round(counts_missing / counts_total * 100, dec_perc)) + ")",
            str(counts_total) + " (" + str(round(counts_total / counts_total * 100, dec_perc)) + ")"
        ]

        df_missing = pd.DataFrame(
            {'Removed measurements, counts (%)': subset_n_perc},
            index=["Missing measurements", "Total"]
        )
        return [df, df_missing]

    except Exception as e:
        return e
