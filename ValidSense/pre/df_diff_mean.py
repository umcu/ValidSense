import pandas as pd
import numpy as np


def df_diff_mean(df: pd.DataFrame, test_device: str = 'Dev1', ref_device: str = 'Dev2'):
    """
    Function to calculate the difference (test - reference) and mean between two devices.
    :param df: (pandas DataFrame) dataframe with reference and test device.
    :param test_device: (str = 'Dev1') column name of Test device.
    :param ref_device: (str = 'Dev2') column name of Reference device.
    :return: (pandas DataFrame) dataframe with difference and mean added as column.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(ref_device, str):
        raise TypeError(f"ref_device is of type {type(ref_device).__name__}, should be str")
    if not isinstance(test_device, str):
        raise TypeError(f"test_device is of type {type(test_device).__name__}, should be str")
    if test_device not in df.columns:
        raise KeyError("test_device not existing in df.")
    if ref_device not in df.columns:
        raise KeyError("ref_device not existing in df.")
    if df[test_device].isnull().values.any():
        raise ValueError("test_device contains missing values")
    if df[ref_device].isnull().values.any():
        raise ValueError("ref_device contains missing values")

    try:
        df['Mean'] = np.mean([df[ref_device], df[test_device]], axis=0)
        # diff = test - ref, see https://www-users.york.ac.uk/~mb55/meas/diffplot.htm
        df['Diff'] = df[test_device] - df[ref_device]
        return df

    except Exception as e:
        return e
