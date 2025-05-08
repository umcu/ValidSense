import pandas as pd


def upload_list_to_dict(upload_list: list, sep: str = ';'):
    """
    Function to convert streamlit file_uploader file to dictionary. Multiple CSV/XLSX files are allowed. Multiple
    sheets in XLSX are seperated.
    :param upload_list: (list) streamlit.file_uploader input with accept_multiple_files=True.
    :param sep: (str = ';') delimiter to use for pandas.read_csv.
    :return: (dict) dict with all uploaded files in pd.DataFrame format.
    """

    # warning
    if len(upload_list) == 0:
        raise Exception("No files are uploaded")
    if not isinstance(sep, str):
        raise TypeError(f"sep is of type {type(sep).__name__}, should be str")

    # empty dict
    all_files_dict = {}
    # load every file and add column with file_name (+ sheet_name)
    try:
        for file in upload_list:
            # name of uploaded file
            file_name = str(file.name)
            # load csv and/or xlsx
            if file.type == 'text/csv':
                # csv is uploaded
                all_files_dict[file_name] = pd.read_csv(filepath_or_buffer=file, sep=sep)
            elif file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                # xlsx is uploaded
                all_sheets_dict = pd.read_excel(io=file, sheet_name=None)   # upload all sheets
                for sheet_name in all_sheets_dict:
                    file_and_sheet_name = str("Sheet:"+sheet_name + "/File:" + file_name)
                    all_files_dict[file_and_sheet_name] = all_sheets_dict[sheet_name]
        return all_files_dict

    except Exception as e:
        return e
