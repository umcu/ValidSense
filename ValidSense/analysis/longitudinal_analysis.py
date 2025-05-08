import pandas as pd
import numpy as np
from ValidSense import analysis

# maximal 100 caches
# @st.experimental_memo(max_entries=100)
def longitudinal_analysis(df: pd.DataFrame, window_unit: str, window_size: int, col_datetime: str = 'Datetime',
                     loa_subtype: str = 'Classic',
                     rep_group_by: str = None,
                     mem_bias_fixed_var: list = None, mem_bias_random_var: list = None, mem_loa_fixed_var: list = None,
                     mem_loa_random_var: list = None):

    """
    Function to calculate the bias and 95% LoA over time. For every step in window_unit in the
    column col_datetime, the bias and 95% LoA are calculated. Rows with time windows where no data is
    available are dropped. Similar for rows when the max of df[col_datetime] exceeds the window size.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param window_unit: (str) window unit in days (D), hours (h) or minutes(m).
    :param window_size: (int) window size.
    :param col_datetime: (str = 'Datetime') column containing both date and time.
    :param loa_subtype: (str = 'Classic') subtype of the limits of agreement analysis for the time series analysis.
    :param rep_group_by: (str = None) if subtype is 'Repeated Measurements': column in dataframe where multiple
    subjects are grouped by.
    :param mem_bias_fixed_var: (list = None) if subtype is 'Mixed-effect': list with fixed effects for bias
    :param mem_bias_random_var: (list = None) if subtype is 'Mixed-effect': list with random effects for bias
    :param mem_loa_fixed_var: (list = None) if subtype is 'Mixed-effect': list with fixed effects for loa
    :param mem_loa_random_var: (list = None) if subtype is 'Mixed-effect': list with random effects for loa
    :return: ([pandas DataFrame, str, statsmodels.regression.mixed_linear_model.MixedLMResultsWrapper,
    statsmodels.regression.mixed_linear_model.MixedLMResultsWrapper, bioinfokit analys stat]) dataframe
    with limits of agreement variant statistics, assumptions and model.

    dataframe with Time Analysis limits of agreement analysis statistics and their
     assumptions.
    """

    # global df_bias_loa
    subtypes = [
        "Classic",
        "Repeated measurements",
        "Mixed-effect",
    ]

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(window_unit, str):
        raise TypeError(f"window_unit is of type {type(window_unit).__name__}, should be str")
    if not isinstance(window_size, int):
        raise TypeError(f"window_size is of type {type(window_size).__name__}, should be int")
    if not isinstance(col_datetime, str):
        raise TypeError(f"col_datetime is of type {type(col_datetime).__name__}, should be str")
    if not isinstance(loa_subtype, str):
        raise TypeError(f"loa_subtype is of type {type(loa_subtype).__name__}, should be str")
    if col_datetime not in df.columns:
        raise KeyError("col_datetime not existing in df")
    if 'Diff' not in df.columns:
        raise KeyError("Diff not existing in df")
    if 'Mean' not in df.columns:
        raise KeyError("Mean not existing in df")
    if loa_subtype not in subtypes:
        raise KeyError("loa_subtype should be of type 'Classic', 'Repeated measurements' or 'Mixed-effect'")
    if df['Diff'].isnull().values.any():
        raise ValueError("Diff contains missing values")
    if df['Mean'].isnull().values.any():
        raise ValueError("Mean contains missing values")
    if window_size <= 0:
        raise Exception("window_size is empty, window_size is not positive number")
    if loa_subtype == 'Repeated measurements':
        if rep_group_by is None:
            raise TypeError(f"rep_group_by should not be None")
        if not isinstance(rep_group_by, str):
            raise TypeError(f"rep_group_by is of type {type(rep_group_by).__name__}, should be str")
        if df[rep_group_by].isnull().values.any():
            raise ValueError("rep_group_by contains missing values")
    if loa_subtype == 'Mixed-effect':
        if not isinstance(mem_bias_fixed_var, list):
            raise TypeError(f"mem_bias_fixed_var is of type {type(mem_bias_fixed_var).__name__}, should be list")
        if not isinstance(mem_bias_random_var, list):
            raise TypeError(f"mem_bias_random_var is of type {type(mem_bias_random_var).__name__}, should be list")
        if not isinstance(mem_loa_fixed_var, list):
            raise TypeError(f"mem_loa_fixed_var is of type {type(mem_loa_fixed_var).__name__}, should be list")
        if not isinstance(mem_loa_random_var, list):
            raise TypeError(f"mem_loa_random_var is of type {type(mem_loa_random_var).__name__}, should be list")
        if len(mem_bias_random_var) == 0:
            raise Exception("mem_bias_random_var is empty, minimal 1 random effect for bias should be included")
        if len(mem_loa_random_var) == 0:
            raise Exception("mem_loa_random_var is empty, minimal 1 random effect for bias should be included")

    try:
        date_first_floor = df[col_datetime].min().floor(freq=window_unit)
        date_last_ceil = df[col_datetime].max().ceil(freq=window_unit)
        count_rows = int((date_last_ceil - date_first_floor) / np.timedelta64(1, window_unit))

        # empty lists
        bias = []
        upper_loa = []
        lower_loa = []
        time_start = []
        time_end = []
        time_bool = []
        model_bias = None
        model_loa = None
        model_rep = None

        # delta is step size for every loop
        for delta in range(0, count_rows):
            # start and end datetime
            filt_start = date_first_floor + pd.Timedelta(value=0 + delta, unit=window_unit)
            filt_end = date_first_floor + pd.Timedelta(value=window_size + delta, unit=window_unit)

            # time index where df is in window
            time_index = ((df[col_datetime] >= filt_start) & (df[col_datetime] < filt_end)).tolist()
            df_filt = df.loc[time_index]

            # limits of agreement analysis subtype
            if loa_subtype == 'Classic':
                # get limits of agreement classic statistics and assumptions
                [df_bias_loa, assumptions] = analysis.loa_classic(df=df_filt)

            elif loa_subtype == 'Repeated measurements':
                # get limits of agreement repeated measurements statistics and assumptions
                [df_bias_loa, assumptions, model_rep] = analysis.loa_repeated_measurements(df=df_filt, group_by=rep_group_by)

            elif loa_subtype == 'Mixed-effect':
                [df_bias_loa, assumptions, model_bias, model_loa] = analysis.loa_mixed_effect_model(
                    df=df_filt,
                    bias_fixed_variable=mem_bias_fixed_var,
                    bias_random_variable=mem_bias_random_var,
                    loa_fixed_variable=mem_loa_fixed_var,
                    loa_random_variable=mem_loa_random_var,
                )

            # extract bias, upper loa, lower loa and time information
            bias.append(df_bias_loa['Bias']['Intercept'])
            upper_loa.append(df_bias_loa['UpperLoA']['Intercept'])
            lower_loa.append(df_bias_loa['LowerLoA']['Intercept'])
            time_start.append(filt_start)
            time_end.append(filt_end)
            time_bool.append(time_index)

        # save in df_bias_loa
        df_bias_loa_time = pd.DataFrame(list(zip(bias, upper_loa, lower_loa, time_start, time_end, time_bool)),
                                 columns=['Bias', 'UpperLoA', 'LowerLoA', 'TimeStart', 'TimeEnd', 'TimeBoolean'])

        # drop rows when the max of df[col_datetime] exceeds the window size
        df_bias_loa_time.drop(
            df_bias_loa_time[
                df_bias_loa_time['TimeEnd'] > df['Datetime']
                .max()
                .ceil(freq=window_unit)
                ]
                .index,
            inplace=True
        )

        # drop rows with nan: window where no data is available
        df_bias_loa_time = df_bias_loa_time.dropna(axis=0, how='any')

        return [df_bias_loa_time, assumptions, model_bias, model_loa, model_rep]

    except Exception as e:
        return e
