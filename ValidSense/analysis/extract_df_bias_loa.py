import pandas as pd


def extract_df_bias_loa(df: pd.DataFrame, df_bias_loa_time: pd.DataFrame, time_start: pd.Timestamp):

    """
    Function to extract bias and 95% LoA from df_bias_loa_time according to time_start. Moreover, filter df
    based on time_start column in df.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param df_bias_loa_time: (pandas DataFrame) dataframe bias and limits of agreement for every step.
    :param time_start: (pandas Timestamp) timestamp to extract.
    :return: ([pandas DataFrame, str]) dataframe with statistics of the Longitudinal Analysis.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(df_bias_loa_time, pd.DataFrame):
        raise TypeError(f"df_bias_loa_time is of type {type(df_bias_loa_time).__name__}, should be pandas DataFrame")
    if not isinstance(time_start, pd.Timestamp):
        raise TypeError(f"time_start is of type {type(time_start).__name__}, should be pandas Timestamp")
    if df_bias_loa_time.empty:
        raise Exception("df_bias_loa_time is empty")

    try:
        # filter based on timebool
        ind = df_bias_loa_time.index[df_bias_loa_time['TimeStart'] == time_start][
            0]  # [0] to extract int instead of Int64Index
        df_bias_loa = pd.DataFrame(columns=['Bias', 'UpperLoA', 'LowerLoA'], index=['Intercept'])  # empty 1x3 dataframe

        # save in df_bias_loa
        df_bias_loa['Bias']['Intercept'] = df_bias_loa_time['Bias'][ind]
        df_bias_loa['UpperLoA']['Intercept'] = df_bias_loa_time['UpperLoA'][ind]
        df_bias_loa['LowerLoA']['Intercept'] = df_bias_loa_time['LowerLoA'][ind]

        # filter df based on time window
        df_filt = df.loc[df_bias_loa_time['TimeBoolean'][ind]]

        return [df_bias_loa, df_filt]

    except Exception as e:
        return e