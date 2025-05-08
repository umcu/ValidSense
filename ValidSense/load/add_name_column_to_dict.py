def add_name_column_to_dict(data_dict: dict):
    """
    Function to add name as column in dictionary.
    :param data_dict: (dict) dict with all loaded files in pandas DataFrame format.
    :return: (dict) dict with all loaded files in pandas DataFrame format with added name column of file.
    """

    # warning
    if not isinstance(data_dict, dict):
        raise TypeError(f"data_dict is of type {type(data_dict).__name__}, should be dict")

    # keys in all_files_dict
    all_files_keys = list(data_dict.keys())

    # add key to df (file_name + sheet_name)
    try:
        for key in all_files_keys:
            data_dict[key].insert(
                loc=0,              # first column
                column="Filename",  # column name
                value=str(key)
            )
        return data_dict

    except Exception as e:
        return e
