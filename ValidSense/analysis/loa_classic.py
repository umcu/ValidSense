import pandas as pd
import numpy as np


def loa_classic(df: pd.DataFrame):
    """
    Function to calculate the bias and limits of agreement statistics according to the classic limits of agreement
    analysis, see https://pubmed.ncbi.nlm.nih.gov/2868172/.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :return: ([pandas DataFrame, str]) dataframe with classic limits of agreement analysis statistics and their
    assumptions.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if 'Diff' not in df.columns:
        raise KeyError("Diff not existing in df")
    if 'Mean' not in df.columns:
        raise KeyError("Mean not existing in df")
    if df['Diff'].isnull().values.any():
        raise ValueError("Diff contains missing values")
    if df['Mean'].isnull().values.any():
        raise ValueError("Mean contains missing values")

    assumptions = [
        True,  # Assumption 0: Normal distribution of the difference
        True,  # Assumption 1: Constant agreement over the measurement range
        True,  # Assumption 2: Independent observations
        False, # Assumption 3: Within-cluster-SD independent of cluster-mean
        False, # Assumption 4: Normal distribution of residuals
        False, # Assumption 5: Homogeneity of residuals
        False, # Assumption 6: Exogeneity of fixed effects.
    ]

    try:
        df_bias_loa = pd.DataFrame(columns=['Bias', 'UpperLoA', 'LowerLoA'], index=['Intercept'])  # empty 1x3 dataframe

        # variables (local)
        z = 1.96                    # z-score of the 95% estimated interval assuming a normal distribution of diff

        # bias
        b0 = np.mean(df['Diff'])    # mean of difference
        std = np.std(df['Diff'], ddof=1)    # standard deviation of difference

        # limits of agreement
        g0 = std * z

        # save in df_bias_loa
        df_bias_loa['Bias']['Intercept'] = b0
        df_bias_loa['UpperLoA']['Intercept'] = b0 + g0
        df_bias_loa['LowerLoA']['Intercept'] = b0 - g0
        df_bias_loa['Std'] = std

        return [df_bias_loa, assumptions]

    except Exception as e:
        return e
