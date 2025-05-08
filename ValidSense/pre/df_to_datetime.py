import pandas as pd


def df_to_datetime(df: pd.DataFrame, separate_datetime: bool, datetime: str = None, time: str = None,
                   date: str = None, format_strftime: str = None, datetime_unit: str = None):
    """
    Function to convert column in dataframe to datetime64[ns] format. Date and time could be in separate columns or in
    one column. Column will be renamed to 'Datetime'. Format of datetime input can be changed.
    :param df: (pandas DataFrame) dataframe to be converted to datetime.
    :param separate_datetime: (bool) True when datetime in separate column. False if datetime is in one column.
    :param datetime: (str = None) column containing both date and time.
    :param time: (str = None) column containing time.
    :param date: (str = None) column containing date.
    :param format_strftime: (str = None) change format input
    (https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior).
    :param datetime_unit: (str = None) unit of datetime (D,s,ms,us,ns) after UNIX epoch start (January 1, 1970,
     at 00:00:00 UTC").
    :return: (pandas DataFrame) dataframe with colum 'Datetime' in format datetime64[ns].
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(separate_datetime, bool):
        raise TypeError(f"separate_datetime is of type {type(separate_datetime).__name__}, should be bool")
    if not separate_datetime:   # datetime in one column
        if not isinstance(datetime, str):
            raise TypeError(f"datetime is of type {type(datetime).__name__}, should be str")
    if separate_datetime:       # date and time in separate columns
        if not isinstance(date, str):
            raise TypeError(f"date is of type {type(date).__name__}, should be str")
        if not isinstance(time, str):
            raise TypeError(f"time is of type {type(time).__name__}, should be str")
    if not isinstance(format_strftime, (str, type(None))):
        raise TypeError(f"format_strftime is of type {type(format_strftime).__name__}, should be str or NoneType")
    if not isinstance(datetime_unit, (str, type(None))):
        raise TypeError(f"datetime_unit is of type {type(datetime_unit).__name__}, should be str or NoneType")

    try:
        # if datetime is in one colum
        if not separate_datetime:
            df[datetime] = pd.to_datetime(
                arg=df[datetime],
                format=format_strftime,
                unit=datetime_unit,
            )
            # rename column time to Datetime
            df.rename(columns={datetime: 'Datetime'}, inplace=True)
            return df
        # if date and time is in separate columns
        elif separate_datetime:
            # from object to datetime64[ns] via str
            df[time] = pd.to_datetime(
                arg=df[date].astype(str) + ' ' + df[time].astype(str),
                format=format_strftime,
                unit=datetime_unit,
            )
            # rename column time to Datetime
            df.rename(columns={time: 'Datetime'}, inplace=True)
            # remove column date
            df = df.drop(columns=date)
            return df

    except Exception as e:
        return e
