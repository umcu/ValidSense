import numpy as np
import pandas as pd
import streamlit as st
from ValidSense import pre

###################################################### STREAMLIT ######################################################
st.set_page_config(layout="wide", page_title="ValidSense | Preprocessing")
st.title("⚙️ Preprocessing")

# session state between pages to save values, and save the inserted value.
for k, v in st.session_state.items():
    st.session_state[k] = v
# see https://discuss.streamlit.io/t/how-to-maintain-inputs-on-changing-endpoints/33474/7

info_c = st.container()             # container for information
warn_c = st.container()             # container for error
tabl_c = st.container()             # container for table
clus_c = st.container()             # container for cluster information
miss_c = st.container()             # container for missing values

# information
info_c.write("**Choose the LoA analysis variant carefully for valid LoA analysis results!**")
with info_c.expander("**Explanation of the preprocessing steps**"):
    st.write(
        """
        * Choose the LoA analysis variant (also used in the Longitudinal analysis).
        * Select the variables indicating:
            * Test device's measurements.
        	* Reference device's measurements.
        	* Cluster variable, such as _Subjects_ (except when using the Classic LoA analysis).
        	* Datetime (when using the Longitudinal analysis).
        * Rename the Test and Reference device's variable to _Dev1_ and _Dev2_.
        * Convert Datetime to the standardised datatype, and rename it to _Datetime_.
        * Remove missing values in the variables utilised in the LoA analysis.
        * Calculate the Difference and Mean between _Dev1_ and _Dev2_.
        """
    )
    st.write(" ")
    st.write(
        """
        **LoA analysis variant**
        \nThe choice of the LoA variant is essential for valid results. For example, investigate which variant is most 
        suitable for correct clustering or non-constant agreement over the measurement range. 
        The _classic LoA analysis_ is unsuitable for clustering or non-constant agreement over the measurement range. 
        More information is on the _Information page_.

       
        """
    )
    LoAvar = pd.DataFrame(
        [
            ['Classic',
             '',
             'Assess agreement in single pair of measurements per patient.'],
            ['Repeated measurements',
             'Clustering',
             'Assess agreement in multiple measurements per patient.'],
            ['Mixed-effects',
             'Clustering (can correct for multiple effects)',
             'Assess agreement based on the mixed-effects LoA analysis, allowing to correct, for example, '
             'multiple measurements per patient or systematic relationship between the difference and mean. '],
            ['Regression of difference',
             'Non-constant agreement over the measurement range',
             'Assess agreement in a single measurement per patient, with a linear relationship between '
             'difference and mean for bias and/or LoA.'],
        ],
        columns=['LoA analysis variant', 'Methodological challenge', 'Intended use'],
    )
    LoAvar.set_index('LoA analysis variant', inplace=True)
    st.table(LoAvar)

    st.write(
        """
        **Mean and Difference**
        \nThe mean and difference are calculated and appended to the table using the following equations:
        \n$Mean = (Dev1 + Dev2) / 2$
        \n$Diff = Dev1 - Dev2$
        """
    )

########################################### GET VARIABLES FROM SESSION STATE ###########################################
if 'dfLoadMerged' in st.session_state:
    df = st.session_state.dfLoadMerged.copy(deep=True)
else:
    warn_c.error("Data not loaded. Go back to the loading page.")
    df = None
    st.stop()

################################################## CHOOSE LOA VARIANT ##################################################
st.sidebar.header("Select LoA variant")
loaTypes = [
    "Classic",
    "Repeated measurements",
    "Mixed-effect",
    "Regression of difference",
]
loaSelect = st.sidebar.selectbox(
    label="Select one of the four LoA analysis variants. Note that this variant is also used for the "
          "_Longitudinal Analysis_.",
    options=loaTypes,
    # label_visibility='collapsed',
    key='loaSelect',
    help=
    """
    The choice of the LoA variant is essential for valid results. For example, investigate which variant is most 
    suitable for correct clustering or non-constant agreement over the measurement range. The _classic LoA analysis_ is 
    unsuitable for clustering or non-constant agreement over the measurement range. More information is on the 
    _Information page_.
    """,
)
st.session_state.loaSelectPreprocessing = loaSelect # to session state

################################################### SELECT VARIABLES ###################################################
variablesOptions = [None] + df.columns.array.tolist()  # list with all the options for the variables of df + None

st.sidebar.subheader("Select variables")

# test variable
oldColDev1 = st.sidebar.selectbox(
    label="Test variable",
    options=variablesOptions,
    key='oldColDev1',
    help="The variable indicating the Test device measurements is renamed to _Dev1_.",
)

# reference variable
oldColDev2 = st.sidebar.selectbox(
    label="Reference variable",
    options=variablesOptions,
    key='oldColDev2',
    help="The variable indicating the Reference device measurements is renamed to _Dev2_.",
)

# cluster variable
groupBy = st.sidebar.selectbox(
    label="Cluster variable",
    options=variablesOptions,
    key='groupBy',
    help="The variable indicating clustering. For example the cluster variable is _Subjects_ when multiple "
         "measurements within one subject are recorded. It is mandatory to select the cluster variable, "
         "except when using the _Classic LoA analysis_."
)
st.session_state.groupByPreprocessing = groupBy

# datetime variable
datetimeOptions = ["Not available", "In a single variable", "In two variables"]

datetimeOptionSel = st.sidebar.radio(
    label="Datetime variable in the dataset",
    options=datetimeOptions,
    # index=datetimeOptions.index(datetimeOptionSel),
    key='datetimeOptionSel',
    # format_func=lambda x: datetimeOptions.get(x),
    help="If the dataset contains date and time information, the corresponding variables should be converted to the "
         "standardized type _Numpy datetime64[ns]_. This applies to both single and double variable cases. Without "
         "datetime information, it is not possible to perform a longitudinal analysis.",
)

if datetimeOptionSel == datetimeOptions[1]:
    # select datetime variable
    datetimeCol = st.sidebar.selectbox(
        label="Datetime variable",
        options=variablesOptions,
        key='datetimeCol',
    )

elif datetimeOptionSel == datetimeOptions[2]:
    # select date and time variable
    dateCol = st.sidebar.selectbox(
        label="Date variable",
        options=variablesOptions,
        key='dateCol',
    )
    timeCol = st.sidebar.selectbox(
        label="Time variable",
        options=variablesOptions,
        key='timeCol',
    )

####################################################### ERRORS ########################################################
# error and stop if oldColDev1 or oldColDev2 is not selected
if oldColDev1 is None or oldColDev2 is None:
    warn_c.error("Select Test and Reference device before continuing")
    st.stop()

# error and stop if groupBy is not selected or consist of missing data

if loaSelect not in ['Classic', 'Regression of difference'] and groupBy is None:
    warn_c.error("Select a variable indicating cluster (e.g. 'Subjects'), to correct for multiple measurements within "
                   "the cluster")
    st.stop()

# error and stop if datetimeCol or dateCol & timeCol are not selected
if datetimeOptionSel == datetimeOptions[1]: # datetime in single variable
    if datetimeCol is None:
        warn_c.error("Select a datetime variable before continuing")
        st.stop()
elif datetimeOptionSel == datetimeOptions[2]:  # date and time in separate variables
    if dateCol is None or timeCol is None:
        warn_c.error("Select a date and time variable before continuing")
        st.stop()

########################################### RENAME TEST AND REFERENCE DEVICE ###########################################
df = pre.df_rename_col(
    df=df,
    column_name_old=oldColDev1,
    column_name_new='Dev1',
)
df = pre.df_rename_col(
    df=df,
    column_name_old=oldColDev2,
    column_name_new='Dev2',
)

######################################### CONVERSION TYPE AND RENAME DATETIME ##########################################
# change format and UNIX
if datetimeOptionSel == datetimeOptions[1] or datetimeOptionSel == datetimeOptions[2]:
    with st.sidebar.expander("**Datetime conversion settings**"):
        # Format
        datetimeForm = st.text_input(  # default None
            label="Format of datetime",
            value='None',
            key='datetimeForm',
            help="The default value of _None_ attempts automated conversion and can be modified to the format "
                 "specified in https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior"
        )
        if datetimeForm == 'None':
            datetimeForm = None
        # UNIX
        if st.checkbox(
                label="UNIX datetime",
                help="Unix or epoch timestamps is the number of seconds that have passed since January 1, 1970, "
                     "at 00:00:00 UTC. Overwrites the _format of datetime_ input.",
                value=False
        ):
            datetimeUnit = 's'  # UNIX is number of seconds passed since January 1, 1970, at 00:00:00 UTC
        else:
            datetimeUnit = None  # false

# conversion to datetime
if datetimeOptionSel == datetimeOptions[1]:  # datetime in single variable
    df = pre.df_to_datetime(
        df=df,  # extract out of session state to prevent that name change
        separate_datetime=False,
        datetime=datetimeCol,
        format_strftime=datetimeForm,
        datetime_unit=datetimeUnit
    )
elif datetimeOptionSel == datetimeOptions[2]:  # date and time in separate variables
    df = pre.df_to_datetime(
        df=df,  # extract out of session state to prevent that name change
        separate_datetime=True,
        date=dateCol,
        time=timeCol,
        format_strftime=datetimeForm,
        datetime_unit=datetimeUnit
    )
else:
    # undo to step before conversion when something went wrong
    df = df.copy(deep=True)

# error
try:
    st.session_state.dfBeforeMissing = df.copy(deep=True)  # copy to create new object
except:
    if datetimeOptionSel == datetimeOptions[1]:  # datetime in single variable
        warn_c.error("Conversion of Datetime is not possible. Please ensure that the **Datetime variable** is "
                       "correctly inserted and review the **Datetime type conversion settings** (consider using _None_ "
                       "for the **format of datetime** whenever applicable).")
        st.stop()
    elif datetimeOptionSel == datetimeOptions[2]:  # datetime in single variable
        warn_c.error("Conversion of Datetime is not possible. Please ensure that the **Date variable** and "
                       "**Time variable** are correctly inserted and review the **Datetime type conversion settings** "
                       "(consider using _None_ for the **format of datetime** whenever applicable).")
        st.stop()

################################################## REMOVE MEASUREMENTS #################################################
st.sidebar.subheader("Remove measurements")

subsetColDef = list(['Dev1', 'Dev2'])  # default
# if loaSelect is not loaTypes[0]:
if loaSelect not in ['Classic', 'Regression of difference']:
    subsetColDef.append(groupBy)

subsetCol = st.sidebar.multiselect(
    label="Select variables utilised in the LoA analysis",
    options=list(df.columns),
    key='subsetCol',
    default=subsetColDef,
    help="It is not permitted to have missing values in the variables utilised for the LoA analysis. These missing "
         "values should be removed from the dataset."
)

# remove missing values in the selected variables (used for the LoA analysis)
df, dfMissing = pre.missing(df=st.session_state.dfBeforeMissing.copy(deep=True), subset_col=subsetCol)

# error
# if loaSelect != 'Classic' and not all(col in subsetCol for col in ['Dev1', 'Dev2', groupBy]):
if loaSelect not in ['Classic', 'Regression of difference'] \
        and not all(col in subsetCol for col in ['Dev1', 'Dev2', groupBy]):
    warn_c.error(f"_Dev1_, _Dev2_ and _{groupBy}_ are not selected in _Select variables utilised in the LoA "
                   f"analysis_ to remove these measurements.")
    st.stop()
# elif loaSelect == 'Classic' and not all(col in subsetCol for col in ['Dev1', 'Dev2']):
elif loaSelect not in ['Classic', 'Regression of difference'] \
        and not all(col in subsetCol for col in ['Dev1', 'Dev2']):
    warn_c.error(f"_Dev1_ and _Dev2_ and are not selected in _Select variables utilised in the LoA analysis_ to "
                   f"remove these measurements.")
    st.stop()
elif df['Dev1'].isnull().values.any():
    warn_c.error("Dev1 contains missing measurements that should be removed. Select _Dev1_ in _Select variables "
                   "utilised in the LoA analysis_ to remove these measurements.")
    st.stop()
elif df['Dev2'].isnull().values.any():
    warn_c.error("Dev2 contains missing measurements that should be removed. Select _Dev2_ in _Select variables "
                   "utilised in the LoA analysis_ to remove these measurements.")
    st.stop()
# elif loaSelect != 'Classic' and df[groupBy].isnull().values.any():
elif loaSelect not in ['Classic', 'Regression of difference'] \
        and df[groupBy].isnull().values.any():
    warn_c.error(f"Cluster variable {groupBy} contains missing measurements that should be removed. Select "
                   f"_{groupBy}_ in _Select variables utilised in the LoA analysis_ to remove these measurements.")
    st.stop()

################################################# DIFFERENCE AND MEAN #################################################

# calculate diff and mean + add to df
df = pre.df_diff_mean(df=df, ref_device='Dev2', test_device='Dev1')

# df to session_state
st.session_state.dfPreprocessing = df.copy(deep=True)

####################################################### DISPLAY ########################################################
tabl_c.header("Table of preprocessed dataset")
tabl_c.dataframe(df)

miss_c.write("**Removed measurements** in counts (percentage): " + str(dfMissing.iloc[0,0]))

# counts per cluster
try:  # only calculate cluster info when groupBy is not None
    count_per_subject = pd.DataFrame({groupBy: df.groupby(groupBy).size().index,
                                      'Number of measurements': df.groupby(groupBy).size().values})
    count_median = np.median(count_per_subject['Number of measurements'])
    count_IQR25 = np.percentile(count_per_subject['Number of measurements'], 25)
    count_IQR75 = np.percentile(count_per_subject['Number of measurements'], 75)
    count_min = np.min(count_per_subject['Number of measurements'])
    count_max = np.max(count_per_subject['Number of measurements'])
    clus_c.header(f"Number of measurements in the cluster _{groupBy}_")
    col1, col2, col3 = clus_c.columns(3)
    col1.metric(label="Median", value=str(count_median))
    col2.metric(label="Inter Quartile Range", value=str(count_IQR25) + "-" + str(count_IQR75))
    col3.metric(label="Minimum - Maximum", value=str(count_min) + "-" + str(count_max))
except:
    pass
