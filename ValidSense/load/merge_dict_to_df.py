import pandas as pd


def merge_dict_to_df(data_dict: dict, file_filter:str = None):
    """
    Function to merge filtered files in dict to pandas DataFrame.
    :param data_dict: (dict) all loaded files in dict containing dataframe.
    :param file_filter: (list or None =None) list of names of dataframe to filter.
    :return: (pandas DataFrame) combined dataframe with filtered files.
    """

    # warning
    if not isinstance(data_dict, dict):
        raise TypeError(f"data_dict is of type {type(data_dict).__name__}, should be dict")
    if not isinstance(file_filter, (list, type(None))):
        raise TypeError(f"file_filter is of type {type(file_filter).__name__}, should be list or NoneType")

    try:
        # create empty list
        data_list = []

        # filter all files
        if file_filter is None:
            all_files_keys = list(data_dict.keys())
        # filter selection based on file_filter
        else:
            all_files_keys = file_filter
        # list append
        for file_or_sheet in all_files_keys:
            data_list.append(data_dict[file_or_sheet])
        # merge to pandas DataFrame
        df = pd.concat(data_list)
        return df

    except Exception as e:
        return e
