import streamlit as st
from ValidSense import load

################################################## DEFAULT SETTINGS ###################################################
fig6 = "ExampleGoodStructureLoading.PNG"

###################################################### STREAMLIT ######################################################
st.set_page_config(layout="wide", page_title="ValidSense | Loading")
st.title("📂 Loading")

info_c = st.container()             # container for information
warn_c = st.container()             # container for error
info_cs = st.sidebar.container()    # container for information
input_cs = st.sidebar.container()   # container for input

# session state between pages to save values, and save the inserted value.
for k, v in st.session_state.items():
    st.session_state[k] = v
# see https://discuss.streamlit.io/t/how-to-maintain-inputs-on-changing-endpoints/33474/7

##################################################### INFORMATION ######################################################
info_c.write("Upload one or multiple Excel files in the sidebar. Check the **file requirements** before uploading.")
with info_c.expander("**File Requirements**"):
    c6a, c6b = st.columns(2)
    c6a.write(
        """
        * **Row**: Every row indicates a new measurement (except for the first row).
        * **Column**: Every column indicates a variable. Mandatory variables indicating
            * Test device's measurements
            * Reference device's measurements
            * Cluster variable, such as ‘Subjects’ (except when using the Classic LoA analysis)
            * Datetime (when using the Longitudinal analysis)
        * **Datetime**: Date and Time could be in one variable (such as in the example), or in two variables and can 
            be merged in the preprocessing page.
        * **Extension**: Excel files are in CSV or XLSX format.
        * **Multiple files**: •	Multiple files: XLSX files could contain multiple sheets. When multiple files or sheets 
            are loaded, these should have the exact variable names across the different sheets.
        * **Merged cells**: Not allowed
        * **Empty cells**: Leave the cell empty when no measurement can be displayed 
            (do not use NAN indicating empty measurement).
        """
    )
    c6b.image(image=fig6, caption='Figure 6: Example of good structured file.')

info_cs.write("_When loading a subsequent dataset with different variable names, press the **F5** button to clear "
              "cached variables and data from the program's memory._")

######################################################## UPLOAD ########################################################
with info_c, st.spinner(text="Uploading files..."):
    uploadList = input_cs.file_uploader(
        label="Upload one or multiple Excel files",
        type={"csv", "xlsx"},
        help="Check the file requirements before uploading",
        accept_multiple_files=True,  # when changed, other function will not work since upload is no longer list
    )

# delimiter for CSV files
with input_cs.expander("**Delimiter for loading CSV files**"):
    sep = st.text_input(
        label="The delimiter or separator in CSV files is a character or sequence of characters that separates the "
             "values or fields in a row. The most commonly used delimiter in CSV files is the comma (,), but other "
             "delimiters such as semicolons (;) can also be used.", #"Specify the delimiter for loading of CSV files",
        key='sep',
        value=';'
    )


# error to upload file and stop if no file or empty list is uploaded
if len(uploadList) == 0:
    warn_c.error("No files have been uploaded")
    st.stop()

with info_c, st.spinner(text="Convert loaded files to Pandas DataFrame..."):
    dataDict = load.upload_list_to_dict(upload_list=uploadList, sep=sep)  # uploaded list to dict
    if isinstance(dataDict, ValueError):
        warn_c.error("The Excel file could not be read. Please ensure that the files have been uploaded correctly "
                       "and that the _Delimiter for loading CSV files_ has been inputted correctly.")
    filenamesAll = list(dataDict.keys())  # list with all filenames all files names
    dataDict = load.add_name_column_to_dict(data_dict=dataDict)  # add name column in dict per df

######################################################## FILTER ########################################################
# filter keys, default all files
with input_cs.expander("**Filter loaded files**"):
    fileFilter = st.multiselect(
        label="The files and/or sheets to be merged into the table used in the _Preprocessing page_ should only "
              "include those that have been filtered",
        options=filenamesAll,
        default=filenamesAll,
    )

# error if keysFilter is empty
if len(fileFilter) == 0:
    warn_c.error("Filtered files and/or sheets to be merged is empty")
    st.stop()
with info_c, st.spinner(text="Filter the loaded files..."):
    # merge dataDict to df
    df = load.merge_dict_to_df(data_dict=dataDict, file_filter=fileFilter)

################################################## DISPLAY MERGED FILE #################################################
st.header("Loaded Table")
st.write("Check if the table is correctly loaded and merged, before continue to the _Preprocessing page_.")
st.dataframe(df)
st.session_state.dfLoadMerged = df.copy() # save in session state

