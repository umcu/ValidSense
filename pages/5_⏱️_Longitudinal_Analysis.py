import pandas as pd
import streamlit as st
import numpy as np
from ValidSense import analysis
import datetime

###################################################### STREAMLIT ######################################################
st.set_page_config(layout="wide", page_title="ValidSense toolbox - Time Series Analysis")
st.title("⏱️Longitudinal Analysis")

# containers main body
info_c = st.container()                 # container for information
warn_c = st.container()                 # container for error
tab_c = st.container()                  # container for table before measurement
long_c = st.container()                 # container for longitudinal analysis
agree_c = st.container()                # container for agreement plot
bland_c = st.container()                # container for bland-altman plot
stat_c = st.container()                 # container for additional LoA analysis statistics
ass_c = st.container()                  # container for assumptions
ts_c = st.container()                   # container for time series

# containers sidebar
info_cs = st.sidebar.container()        # container for information
show_cs = st.sidebar.container()        # container for show checkboxes
exp_cs = st.sidebar.container()         # container for expanders
ass_show_cs = st.sidebar.container()    # container sidebar for assumptions show
ass_exp_cs = st.sidebar.container()     # container sidebar for assumptions expander

# session state between pages to save values, and save the inserted value.
for k, v in st.session_state.items():
    st.session_state[k] = v
# see https://discuss.streamlit.io/t/how-to-maintain-inputs-on-changing-endpoints/33474/7

# information
info_c.write(
    """
    The newly developed Longitudinal analysis can assess non-constant agreement over time. The longitudinal analysis 
    involves breaking down a dataset into smaller parts over time and applying existing LoA analysis to each part. 
    A moving time window is applied, and based on the data included in the window, the bias and 95% LoA are calculated 
    for each time window. The **agreement plot** graphical visualises the results of the longitudinal analysis. 
    A window can be selected using the time slider, shown in the **Bland-Altman plot of a selected window**, and 
    allows the user to navigate through the time domain. More information is on the _Information page_. 
    In addition traditional **Time series plots** are also available (independent from the Longitudinal analysis), 
    to show the datapoints and trendlines of each cluster.
    """
)

info_cs.write("_Download image in the upper right corner of the figures (:camera:)._")

# default settings for downloading
height = 700
width = 1200
scale = 6

########################################### GET VARIABLES FROM SESSION STATE ###########################################
if 'dfPreprocessing' in st.session_state:
    df = st.session_state.dfPreprocessing.copy(deep=True)
else:
    warn_c.error("Data not preprocessed. Go back to the preprocessing page.")
    df = None
    st.stop()
loaSelect = st.session_state.loaSelectPreprocessing
groupBy = st.session_state.groupByPreprocessing

# error
if 'Datetime' not in df.columns:
    warn_c.error("Datetime is not in df, go back to preprocessing.")
    st.stop()
elif df.dtypes['Datetime'] != 'datetime64[ns]':
    warn_c.error(f"Datetime should be datetime64[ns], go back to preprocessing")

########################################## DISPLAY DATAFRAME BEFORE ANALYSIS ###########################################
if show_cs.checkbox("Show dataset table"):
    tab_c.header("Dataset table")
    tab_c.dataframe(df)

################################################# LOA ANALYSIS SETTINGS ################################################
if loaSelect == 'Regression of difference':
    warn_c.error("The _Regression of difference_ variant of the LoA analysis is unsuitable for longitudinal "
                 "analysis, as constant agreement over the measurement range is assumed. Please choose the _Classic_, "
                 "_Repeated measurements_, or _Mixed-effects_ LoA analysis variant on the _Preprocessing page_.")
    st.stop()

if loaSelect == 'Mixed-effect':
    with exp_cs.expander("**Mixed-effect LoA analysis settings**"):
        biasFixedLongitudinalVar = st.multiselect(
            label="Select fixed variables for bias model",
            options=df.columns,
            key='biasFixedLongitudinalVar',
            help="Fixed effects for bias."
        )

        # biasRandomLongitudinalVar = st.multiselect(
        #     label="Select random variables for bias model",
        #     options=df.columns,
        #     key='biasRandomLongitudinalVar',
        #     default=groupBy,
        #     help="Random effect for bias. Minimal one random effect is required, and default is cluster variable."
        # )

        loaFixedLongitudinalVar = st.multiselect(
            label="Select fixed variables for 95% LoA model",
            options=df.columns,
            key='loaFixedLongitudinalVar',
            help="Fixed effects for 95% LoA."
        )
        # loaRandomLongitudinalVar = st.multiselect(
        #     label="Select random variables for 95% LoA model",
        #     options=df.columns,
        #     key='loaRandomLongitudinalVar',
        #     default=groupBy,
        #     help="Random effect for 95% LoA. Minimal one random effect is required, and default is cluster variable."
        # )

    # # error if biasRandomLongitudinalVar is empty list
    # if len(biasRandomLongitudinalVar) == 0:
    #     warn_c.error("Select minimally one random variable for bias before continuing.")
    #     st.stop()
    #
    # # error if loaRandomLongitudinalVar is empty list
    # if len(loaRandomLongitudinalVar) == 0:
    #     warn_c.error("Select minimally one random variable for 95% LoA before continuing.")
    #     st.stop()
else:
    biasFixedLongitudinalVar = None
    biasRandomLongitudinalVar = None
    loaFixedLongitudinalVar = None
    loaRandomLongitudinalVar = None

################################################# LONGITUDINAL ANALYSIS ################################################
with exp_cs.expander("**Longitudinal analysis settings**"):
    st.write(f"Longitudinal analysis is based on the {groupBy} LoA analysis variant.")

    windowUnitOptions = {'D': 'Day(s)', 'h': 'Hour(s)'}  # options for window unit
    windowUnit = st.selectbox(
        label="Window unit",
        options=windowUnitOptions,
        format_func=lambda x: windowUnitOptions.get(x),
        index=0,
        key='windowUnit',
        help="Select window size unit. More information:"
             "https://numpy.org/doc/stable/reference/arrays.datetime.html#datetime-units"
    )

    windowSize = st.text_input(
        label="Window size",
        value=1,
        key='windowSize',
        help="Select the amount of " + str(windowUnit) + ". The table is filtered based on this window size."
        )

    # filter based on cluster variable
    df_filtered = st.session_state.dfPreprocessing.copy(deep=True)
    group_options_time_series = df_filtered[groupBy].unique()  # unique subjects
    group_selection = st.multiselect(
        label=f"Filter _{groupBy}_ for the longitudinal analysis",
        options=list(group_options_time_series),
        default=group_options_time_series,  # default all
        key='group_selection',
        help=f"The Longitudinal analysis only includes the measurements of {groupBy} that have been filtered, and they "
             f"are the ones displayed in the **Agreement plot** and **Difference plot**. Filtering does not impact the "
             f"Time series plot.",
    )

    # error and stop
    try:
        windowSize = int(windowSize)
    except:
        warn_c.error("Window size is not of type integer or is empty.")
        st.stop()

    if windowSize <= 0:
        warn_c.error("Window size is not a positive number.")
        st.stop()

    if len(group_selection) == 0:
        warn_c.error(f"The cluster variable for the longitudinal analysis filtering is empty. Please select minimal "
                     f"one _{groupBy}_ before continue.")
        st.stop()

    # filter cluster
    df_filtered = df_filtered[df_filtered[groupBy].isin(group_selection)]
    df_filtered = df_filtered.sort_values([groupBy], ascending=[True])  # sort

    with info_c, st.spinner(text="Calculating longitudinal analysis statistics..."):
        # get longitudinal analysis statistics and assumptions
        [dfBiasLoaTime, assumptions, modelBias, modelLoa, modelRep] = analysis.longitudinal_analysis(
            df=df_filtered,
            col_datetime='Datetime',
            window_unit=windowUnit,
            window_size=windowSize,
            loa_subtype=loaSelect,
            rep_group_by=groupBy,
            mem_bias_fixed_var=biasFixedLongitudinalVar,
            mem_bias_random_var=[groupBy],
            mem_loa_fixed_var=loaFixedLongitudinalVar,
            mem_loa_random_var=[groupBy]
        )

    # error and stop if window is larger than window available in dataset (dfBiasLoaTime is empty)
    if dfBiasLoaTime.empty:
        warn_c.error(f"The window size exceeds the time range covered by the data, or the number of {groupBy} included "
                     f"after filtering is too low.")
        st.stop()
    elif dfBiasLoaTime['TimeStart'].min() == dfBiasLoaTime['TimeStart'].max():
        warn_c.error("The window size contains all data points. Select smaller window to calculate the "
                     "longitudinal analysis.")
        st.stop()

    if st.checkbox(label="Show additional information about the Longitudinal analysis"):
        agree_c.subheader("Additional information of the Longitudinal analysis")
        agree_c.dataframe(dfBiasLoaTime)

# add fits and residuals to df if exist in locals and is not None
if 'modelBias' in locals() and modelBias != None:
    df = analysis.df_add_model_fits_residuals(df, modelBias, 'Bias')

if 'modelLoa' in locals() and modelLoa != None:
    df = analysis.df_add_model_fits_residuals(df, modelLoa, '95LoA')

#################################################### AGREEMENT PLOT ####################################################
if show_cs.checkbox(label="Show Agreement plot", value=True,
                    help="Based on longitudinal analysis. Shows data of all windows"):
    with exp_cs.expander("**Agreement plot settings**"):
        # title
        titleAgreementPlot = st.text_input(
            "Title",
            value="Agreement plot",
            key='titleAgreementPlot',
            help="Change title of the Agreement plot",
        )
        # x label
        labelXAgreementPlot = st.text_input(
            "Label x-axis",
            value="Time",
            key='labelXAgreementPlot',
            help="Change label of the x-axis",
        )
        # y label
        labelYAgreementPlot = st.text_input(
            "Label y-axis",
            value="Difference",
            key='labelYAgreementPlot',
            help="Change label of the y-axis",
        )


    with info_c, st.spinner(text="Preparing agreement plot..."):
        figAgreementPlot = analysis.fig_agreement_plot(
            df_bias_loa_time=dfBiasLoaTime,
            title_text=titleAgreementPlot,
            xlabel=labelXAgreementPlot,
            ylabel=labelYAgreementPlot,
        )

    # agree_c.header("Agreement plot")
    fileNameTime = str("AgreementPlot" + "_" + "_" + loaSelect.replace(" ","") + "_" +
                       datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    agree_c.plotly_chart(figure_or_data=figAgreementPlot,
                      config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameTime,
                                                       'height': height,'width': width, 'scale': scale}})

#################################################### SELECT WINDOW #####################################################
# select start time of the window for the Bland-Altman plot
sliderTimeStart = agree_c.select_slider(
    label="**Window start time**",
    options=dfBiasLoaTime['TimeStart'],
    key='sliderTimeStart',
    help="Time-slider to navigate through the agreement plot and show the Bland-Altman plot of a selected time window."
)

# show the selected time window, in 3 columns
sliderIndex = dfBiasLoaTime[dfBiasLoaTime['TimeStart'] == sliderTimeStart].index[0]  # extract data from selected window
col1, col2, col3 = agree_c.columns(3)
col1.metric(label="Start window", value=str(dfBiasLoaTime['TimeStart'][sliderIndex]))
col2.metric(label="End window", value=str(dfBiasLoaTime['TimeEnd'][sliderIndex]))
col3.metric(label="Window size", value=str(str(windowSize) + " " + windowUnitOptions[windowUnit]))

# convert dfBiasLoaTime to dfWindow
[dfBiasLoa, dfWindow] = analysis.extract_df_bias_loa(
    df=df_filtered,
    df_bias_loa_time=dfBiasLoaTime,
    time_start=sliderTimeStart
)
################################################## BLAND-ALTMAN PLOT ###################################################
if show_cs.checkbox(label="Show Bland-Altman plot", value=True,
                    help="Based on longitudinal analysis. Shows data of one selected window"):
    with exp_cs.expander("**Bland-Altman plot settings**"):
        # cluster
        groupColorLongitudinal = st.selectbox(
            label="Colour variable",
            options=[None] + dfWindow.columns.array.tolist(),
            key='groupColorLongitudinal',
            help="Colour a variable. For example, trends in the data might be identified by selecting the "
                 "cluster variable."
        )
        heatmapLongitudinal = st.checkbox(
            label="Heatmap",
            value=False,
            key='heatmapLongitudinal',
            help="Show the density of measurements in different regions to prevent overplotting in large datasets.",
        )
        # heatmap & marginal distribution plot
        if heatmapLongitudinal:
            nbinsLongitudinal = st.number_input(
                label="Number of bins",
                min_value=0,
                key='nbinsLongitudinal',
                help="The division of the data range into a fixed number of intervals, which are then represented by "
                     "the blue boxes. If _0_, the number of bins are automatically calculated.",
            )
            if nbinsLongitudinal == 0:
                nbinsLongitudinal = None
            marginalLongitudinal = None
        else:
            nbinsLongitudinal = None
            marginalLongitudinal = st.selectbox(
                label="Marginal distribution subplot",
                options=[None, 'rug', 'box', 'violin', 'histogram'],
                key='marginalLongitudinal',
                help="Add marginal distribution subplots to the Bland-Altman plot for pattern recognition. More "
                     "information https://plotly.com/python-api-reference/generated/plotly.express.scatter.html."
            )
        # title
        titleLongitudinalBlandAltmanPlot = st.text_input(
            "Title",
            value="Bland-Altman plot of the selected window",
            key='titleLongitudinalBlandAltmanPlot',
            help="Change title of the Bland-Altman plot",
        )
        # x label
        labelXLongitudinalBlandAltmanPlot = st.text_input(
            "Label x-axis",
            value="Mean",
            key='labelXBlandAltmanPlot',
            help="Change label of the x-axis",
        )
        # y label
        labelYLongitudinalBlandAltmanPlot = st.text_input(
            "Label y-axis",
            value="Difference",
            key='labelYBlandAltmanPlot',
            help="Change label of the y-axis",
        )

        if st.checkbox(label="Show additional information about the LoA analysis"):
            bland_c.subheader("Additional information of the LoA analysis")
            bland_c.dataframe(dfBiasLoa)
            # information of modelBias and modelLoa
            if modelBias is not None:
                bland_c.write("**Model bias**")
                bland_c.write(modelBias.summary())
            if modelLoa is not None:
                bland_c.write("**Model 95% LoA**")
                bland_c.write(modelLoa.summary())
            if modelRep is not None:
                bland_c.write("**ANOVA model for Repeated Measurements**")
                bland_c.write(modelRep.anova_summary)

    # bland altman plot display
    with info_c, st.spinner(text="Preparing Bland-Altman plot..."):
        figLongitudinalBlandAltmanPlot = analysis.fig_bland_altman_plot(
            df=dfWindow,
            df_bias_loa=dfBiasLoa,
            x='Mean',
            y='Diff',
            title_text=titleLongitudinalBlandAltmanPlot,
            heatmap=heatmapLongitudinal,
            heatmap_nbins=nbinsLongitudinal,
            marginal=marginalLongitudinal,
            xlabel=labelXLongitudinalBlandAltmanPlot,
            ylabel=labelYLongitudinalBlandAltmanPlot,
            group_color=groupColorLongitudinal,
        )
        # bland_c.header("Bland-Altman plot of selected window")
        fileNameLongitudinalBlandAltmanPlot = str("LongitudinalBlandAltmanPlot" + "_" +
                                                  loaSelect.replace(" ", "") +"_" +
                                                  datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        bland_c.plotly_chart(figure_or_data=figLongitudinalBlandAltmanPlot,
                           config={'toImageButtonOptions': {'format': 'png',
                                                            'filename': fileNameLongitudinalBlandAltmanPlot,
                                                            'height': height, 'width': width, 'scale': scale}})

################################################## DISPLAY ASSUMPTIONS #################################################
ass_c.header("Check assumptions")

# default all tools off
test_histogram = False
test_qq_plot = False
test_scatterplot = False
test_residualplot = False
test_within_cluster_SD_plot = False
test_covariance = False

# specific asssumptions and how to test
fig7 = "HistogramQQplotPositiveSkew.png"
fig8 = "Examp_non_const_agreem_meas_range_2023_04_25_13_29_42.png"
fig9 = "Examp_Within_cluster_SD_2023_04_23_14_17_43.png"

if assumptions[0]:
    with ass_c.expander("**Normal distribution of the difference** assumption: Check the _Histogram_ and _Q-Q plot_"):
        c7a, c7b = st.columns(2)
        c7a.write(
            """
            \nThe precision is correctly described as 95% of the data points fall within the 95% LoA. When the 
            differences are highly skewed (see Figure 6), it may be appropriate to consider non-parametric 95% LoA, 
            as described by [Frey et al (2020)](https://www.mdpi.com/2571-905X/3/3/22).
            \n**Histogram**: if the data is normally distributed, the histogram will resemble a bell curve with a 
            symmetrical shape.
            \n**Q-Q plo**t: if the data is normally distributed, the points will form a straight line.
            """
        )
        c7b.image(image=fig7, caption='Figure 7: Example of a positive (right) skewed distribution in a histogram and '
                                      'Q-Q plot.')
        test_histogram = True
        test_qq_plot = True

if assumptions[1]:
    with ass_c.expander("**Constant agreement over the measurement range** assumption: Check the _Scatterplot_"):
        c8a, c8b = st.columns(2)
        c8a.write(
            """
            \nThe variability of differences is not dependent on the mean. If the variability of differences increases 
            with an increase in the mean, it can result in too wide 95% LoA for low values and too small 95% LoA for 
            high values (see Figure below). Use the _regression of difference_ LoA analysis to correct 
            for non-constant agreement over the measurement range.
            \n**Scatterplot**: if the data has constant agreement over the measurement range, there should be no 
            systematic relationship between the difference and mean.
            """
        )
        c8b.image(image=fig8, caption='Figure 8: Example of a Bland-Altman plot with a non-constant agreement in '
                                      'respiratory rate measurements. The variability increases with the mean of the '
                                      'respiratory rate. The regression of difference LoA analysis represents the '
                                      'systematic relationship between the difference and mean.')
        test_scatterplot = True

if assumptions[2]:
    with ass_c.expander("**Independent observations** assumption: Check the data structure"):
        st.write(
            """
            \nMeasurements are independent of one another. For example, when multiple measurements are recorded per 
            subject, the measurements become dependent and violate the independence assumption. Failing to correct for 
            this dependence can result in 95% LoA that are too narrow and do not accurately represent the precision of 
            the measurements. The _repeated measurements_ or _mixed-effect_ LoA analysis can correct this violation by 
            incorporating the within-cluster-SD.
            """
        )

if assumptions[3]:
    with ass_c.expander("**Within-cluster-SD independent of cluster-mean** assumption:  Check the _Within-cluster-SD "
                        "plot_"):
        c9a, c9b = st.columns(2)
        c9a.write(
            """
            \nThe within-cluster standard deviation (SD) of the difference should be independent of the cluster-mean. 
            A constant variability over the multiple measurements is assumed to represent the precision of the 
            measurements (see Figure below). Violation of non-constant variability may be corrected using a 
            logarithmic transformation.
            \n**Within-cluster-SD plot**: The SD on the y-axis should be constant across the subject-mean on the x-axis.
            """
        )
        c9b.image(image=fig9, caption='Figure 9: Example of within-cluster standard deviation plot, with ‘Subjects’ as '
                                      'cluster variable. The within-cluster standard deviation (SD) is plotted on the '
                                      'y-axis, and the cluster-mean on the x-axis.')
        test_within_cluster_SD_plot = True

if assumptions[4]:
    with ass_c.expander("**Normal distribution of residuals** assumption: Check the _Histogram_ and _Q-Q plot_"):
        st.write(
            """
            \nThe residuals represent the difference between the actual data points and the values predicted by the 
            model. The residuals should be normally distributed with a mean of zero to satisfy the linear regression 
            model's assumptions. When the residuals are not normally distributed, it can lead to biased estimates and 
            inaccurate predictions. Correcting the SD may be appropriate when the residuals are non-uniform 
            distributed, as 
            [Maas & Hox (2004)](https://www.sciencedirect.com/science/article/abs/pii/S0167947303001816) described.
            \n**Histogram**: if the data is normally distributed, the histogram will resemble a bell curve with a 
            symmetrical shape.
            \n**Q-Q plot**: if the data is normally distributed, the points will form a straight line.
            """
        )
        test_histogram = True
        test_qq_plot = True

if assumptions[5]:
    with ass_c.expander("**Homogeneity of residuals** assumption: Check the _Residual plot_"):
        st.write(
            """
            \nThe homogeneity of residuals ensures that the variance of the residuals is constant across the 
            differences. Heteroscedasticity violates the assumption of independent data and suggests that some 
            grouping is present in the dataset. As a result, this can lead to a biased estimation of the 
            regression coefficients, impacting the accuracy and precision estimates.
            \n**Residual plot**: A constant variance across every level of the mean must be seen to conclude that the 
            variance of the residuals is independent.
            """
        )
        test_residualplot = True

if assumptions[6]:
    with ass_c.expander("**Exogeneity** assumption: Check the _covariance_"):
        st.write(
            """
            \nExogeneity ensures that the predictor variables (such as _subjects_) are not affected by the errors in 
            the model. If the exogeneity assumption is violated, it can lead to influenced estimates of the regression 
            coefficients, impacting the accuracy and precision estimates.
            \n**Covariance**: The covariance between the _fixed effect_ and the _residuals_, as well as between the 
            _fixed effect_ and _random effects_, should be zero.
            """
        )
        test_covariance = True

################################################## CHECK ASSUMPTIONS ###################################################
ass_show_cs.header("Tools for checking assumptions in the selected window")
# Histogram
if test_histogram:
    if ass_show_cs.checkbox(label="Show histogram"):
        with ass_exp_cs.expander("**Histogram settings**"):
            # number of bins
            histNumberBinsLongitudinal = st.number_input(
                label="Number of bins",
                min_value=0,
                max_value=len(dfWindow),
                value=0,
                key="histNumberBinsLongitudinal",
                help="Number of bins of the histogram. Default (0) is automatic. More information: "
                     "https://plotly.github.io/plotly.py-docs/generated/plotly.express.histogram.html"
            )
            # column for histogram
            histColumnLongitudinal = st.selectbox(
                label="Select variable",
                options=dfWindow.columns,
                index=dfWindow.columns.get_loc('Diff'),
                key="histColumnLongitudinal",
                help="Variable to show the distribution of the values. More information: "
                     "https://plotly.github.io/plotly.py-docs/generated/plotly.express.histogram.html"
            )

            # error and stop if histColumn is not selected
            if histColumnLongitudinal is None:
                warn_c.error("Select a variable to visualise distribution in the histogram before continuing.")
                st.stop()

        # histogram
        with info_c, st.spinner(text="Preparing histogram..."):
            figHistogramLongitudinal = analysis.fig_histogram(
                df=dfWindow,
                column=histColumnLongitudinal,
                number_bins=histNumberBinsLongitudinal,
            )

            fileNameHistogramLongitudinal = str("Histogram" + "_" + loaSelect.replace(" ", "") + "_" +
                                    datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figHistogramLongitudinal,
                               config={'toImageButtonOptions': {'format': 'png',
                                                                'filename': fileNameHistogramLongitudinal,
                                                                'height': height, 'width': width, 'scale': scale}})

# Q-Q plot (default = 'Diff')
if test_qq_plot:
    if ass_show_cs.checkbox(label="Show Q-Q plot"):
        with ass_exp_cs.expander("**Q-Q plot settings**"):
            # column for qq-plot
            qqPlotColumnLongitudinal = st.selectbox(
                label="Select variable",
                options=dfWindow.columns,
                index=dfWindow.columns.get_loc('Diff'),
                key='qqPlotColumnLongitudinal',
                help="Variable to show the distribution of the values. More information: "
                     "https://www.statsmodels.org/dev/generated/statsmodels.graphics.gofplots.qqplot.html"
            )

            # reference line (default: 's')
            qqPlotLineLongitudinal = st.selectbox(
                label="Reference line",
                options=[None, '45', 's', 'r', 'q'],
                index=2,
                key='qqPlotLineLongitudinal',
                help="Select from options: "
                     "No reference line is added to the plot (None), "
                     "45-degree line (45), "
                     "Standardized line, the expected order statistics are scaled by the standard deviation of the "
                     "given sample and have the mean added to them (s), "
                     "A regression line is fit (r), "
                     "A line is fit through the quartiles (q). "
                     "More information: "
                     "https://www.statsmodels.org/dev/generated/statsmodels.graphics.gofplots.qqplot.html."
            )

            # fit
            qqPlotFitLongitudinal = st.checkbox(
                label="Standardized data",
                value=True,
                key='qqPlotFitLongitudinal',
                help="The quantiles are formed from the standardized data, more information: "
                     "https://www.statsmodels.org/dev/generated/statsmodels.graphics.gofplots.qqplot.html"
            )

        # error and stop if qqPlotColumn is not selected
        if qqPlotColumnLongitudinal is None:
            warn_c.error("Select a variable to visualise distribution in the Q-Q plot before continuing.")
            st.stop()

        # qq-plot
        with info_c, st.spinner(text="Preparing Q-Q plot..."):
            figQQPlotLongitudinal = analysis.fig_qq_plot(
                df=dfWindow,
                column=qqPlotColumnLongitudinal,
                line=qqPlotLineLongitudinal,
                fit=qqPlotFitLongitudinal,
            )
            fileNameQQplotLongitudinal = str("Q-Q plot" + "_" + loaSelect.replace(" ", "") + "_" +
                                 datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figQQPlotLongitudinal,
                               config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameQQplotLongitudinal,
                                                                'height': height, 'width': width, 'scale': scale}})

# Scatterplot
if test_scatterplot:
    if ass_show_cs.checkbox(label="Show scatterplot"):
        with ass_exp_cs.expander("**Scatterplot settings**"):
            scatterGroupColorLongitudinal = st.selectbox(
                label="Colour variable",
                options=[None] + dfWindow.columns.array.tolist(),
                index=0,
                key='scatterGroupColorLongitudinal',
                help="Colour a variable. For example, trends in the data might be identified by selecting the "
                     "cluster variable."
            )

            # marginal distribution plot
            marginalScatterLongitudinal = st.selectbox(
                label="Marginal distribution subplot",
                options=[None, 'rug', 'box', 'violin', 'histogram'],
                key='marginalScatterLongitudinal',
                help="Add marginal distribution subplots to the Bland-Altman plot for pattern recognition. More "
                     "information https://plotly.com/python-api-reference/generated/plotly.express.scatter.html."
            )
            # title
            titleScatterPlotLongitudinal = st.text_input(
                "Title",
                value="Scatterplot",
                key='titleScatterPlotLongitudinal',
                help="Change title of the scatterplot",
            )
            # x label
            labelXScatterPlotLongitudinal = st.text_input(
                "Label x-axis",
                value="Mean",
                key='labelXScatterPlotLongitudinal',
                help="Change label of the x-axis",
            )
            # y label
            labelYScatterPlotLongitudinal = st.text_input(
                "Label y-axis",
                value="Difference",
                key='labelYScatterPlotLongitudinal',
                help="Change label of the y-axis",
            )

        # Scatterplot
        with info_c, st.spinner(text="Preparing Scatterplot..."):
            figScatterPlotLongitudinal = analysis.fig_scatter_plot(
                df=dfWindow,
                x='Mean',
                y='Diff',
                title_text=str(titleScatterPlotLongitudinal),
                marginal=marginalScatterLongitudinal,
                xlabel=labelXScatterPlotLongitudinal,
                ylabel=labelYScatterPlotLongitudinal,
                group_color=scatterGroupColorLongitudinal,
            )

            fileNameScatterplotLongitudinal = str("Scatterplot" + "_" + loaSelect.replace(" ","") + "_" +
                                      datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figScatterPlotLongitudinal,
                               config={'toImageButtonOptions': {'format': 'png',
                                                                'filename': fileNameScatterplotLongitudinal,
                                                                'height': height, 'width': width,'scale': scale}})

# Residual plot
if test_residualplot:
    if ass_show_cs.checkbox(label="Show residual plot"):
        with ass_exp_cs.expander("**Residual plot settings**"):
            # x-axis
            residualPlotXLongitudinal = st.selectbox(
                label="Fitted values of the model",
                options=[None] + dfWindow.columns.array.tolist(),
                index=dfWindow.columns.get_loc('model95LoAFittedValues'),
                key='residualPlotXLongitudinal',
                help="Fitted values of the model on the x-axis",
            )

            residualPlotYLongitudinal = st.selectbox(
                label="Residuals of the model",
                options=dfWindow.columns.array.tolist(),
                index=dfWindow.columns.get_loc('model95LoAResiduals'),
                key='residualPlotYLongitudinal',
                help="Residuals of the model on the y-axis",
            )

        # error and stop if residualPlotX or residualPlotY is not selected
        if residualPlotXLongitudinal is None or residualPlotYLongitudinal is None:
            warn_c.error("Select variables indicating fitted values and/or residuals for the residual plot "
                         "before continuing.")
            st.stop()

        # Residual plot
        with info_c, st.spinner(text="Preparing Residual plot..."):
            figResidualPlotLongitudinal = analysis.fig_residual_plot(
                df=dfWindow,
                fits=residualPlotXLongitudinal,
                residuals=residualPlotYLongitudinal,
            )
            fileNameResidualPlotLongitudinal = str("Residual plot" + "_" + loaSelect.replace(" ","") + "_" +
                                       datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figResidualPlotLongitudinal,
                               config={'toImageButtonOptions': {'format': 'png',
                                                                'filename': fileNameResidualPlotLongitudinal,
                                                                'height': height, 'width': width,'scale': scale}})

# Within-cluster-SD plot
if test_within_cluster_SD_plot:
    if ass_show_cs.checkbox(label="Show within-cluster-SD plot"):
        with ass_exp_cs.expander("**Within-cluster-SD plot settings**"):

            withinGroupStdPlotGroupLongitudinal = st.selectbox(
                label="Cluster variable",
                options=dfWindow.columns.array.tolist(),
                index=dfWindow.columns.get_loc(groupBy),
                key='withinGroupStdPlotGroupLongitudinal',
                help="Check the within-cluster standard deviation."
            )

        # error and stop if withinGroupStdPlotGroup is not selected
        if withinGroupStdPlotGroupLongitudinal is None:
            warn_c.error("Select the cluster variable in the within-cluster-SD plot before continuing.")
            st.stop()

        # Within-Group Std plot
        with info_c, st.spinner(text="Preparing Within-cluster-SD plot..."):
            figWithinGroupStdPlotLongitudinal = analysis.fig_within_group_std_plot(
                df=dfWindow,
                group=withinGroupStdPlotGroupLongitudinal)

            fileNameWithinGroupStdPlotLongitudinal = str("Within-cluster-SD plot" + "_" + loaSelect.replace(" ","") +
                                                         "_" + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figWithinGroupStdPlotLongitudinal,
                               config={'toImageButtonOptions': {'format': 'png',
                                                                'filename': fileNameWithinGroupStdPlotLongitudinal,
                                                                'height': height,'width': width, 'scale': scale}})
# Covariance
if test_covariance:
    if ass_show_cs.checkbox(label="Show covariance"):
        with ass_exp_cs.expander("**Covariance settings**"):
            covXLongitudinal = st.selectbox(
                label="Fixed effect variable",
                options=[None] + dfWindow.columns.array.tolist(),
                index=0,
                key="covXLongitudinal",
                help="Measure the relationship between variables by the covariance."
            )
            covYLongitudinal = st.selectbox(
                label="Select random effect or residual variable",
                options=[None] + dfWindow.columns.array.tolist(),
                index=0,
                key='covYLongitudinal',
            )

        # error and stop if covX or covY is not selected
        if covXLongitudinal is None or covYLongitudinal is None:
            warn_c.error("Select the variables for covariance before continuing.")
            st.stop()
        with info_c, st.spinner(text="Preparing Covariance calculation..."):
            covarianceLongitudinal = np.cov(dfWindow[covXLongitudinal], dfWindow[covYLongitudinal])[0][1]
            covariance_roundLongitudinal = round(covarianceLongitudinal, 2)
            ass_c.write(f"**Covariance** between _{covXLongitudinal}_ and _{covYLongitudinal}_: "
                        f"**{covariance_roundLongitudinal}**")

################################################### TIME SERIES PLOT ###################################################
if show_cs.checkbox(label="Show Time series plot", value=True, help="Independent of longitudinal analysis"):
    with exp_cs.expander("**Time series plot settings**"):
        window_size_trendline = st.number_input(
            label="Window trendline",
            min_value=0,
            value=5,
            key='window_size_trendline',
            help="Number of measurements included in the window, for calculating the median moving trendline. If the "
                 "window size is larger than the number of measurements within a cluster, the trendline is not showed."
        )

        time_series_option = {
            "dev1": "Scatter Dev1",
            "dev2": "Scatter Dev2",
            "dev1_dev2": "Scatter Dev1 & Dev2",
            "dev1trend": "Trend Dev1",
            "dev2trend": "Trend Dev2",
            "dev1trend_dev2trend": "Trend Dev1 & Dev2",
            "dev1_dev2_dev1trend_dev2trend": "Scatter & trend Dev1 & Dev2",
        }

        time_series_radio = st.radio(
            label="Scatter and/or trendline of the datapoints",
            options=time_series_option,
            format_func=lambda x: time_series_option.get(x),
            index=5,
            key='time_series_radio',
            )
        if time_series_radio == "dev1":
            show_dev1 = True
            show_dev2 = False
            show_dev1_trend = False
            show_dev2_trend = False
        elif time_series_radio == "dev2":
            show_dev1 = False
            show_dev2 = True
            show_dev1_trend = False
            show_dev2_trend = False
        elif time_series_radio == "dev1_dev2":
            show_dev1 = True
            show_dev2 = True
            show_dev1_trend = False
            show_dev2_trend = False
        elif time_series_radio == "dev1trend":
            show_dev1 = False
            show_dev2 = False
            show_dev1_trend = True
            show_dev2_trend = False
        elif time_series_radio == "dev2trend":
            show_dev1 = False
            show_dev2 = False
            show_dev1_trend = False
            show_dev2_trend = True
        elif time_series_radio == "dev1trend_dev2trend":
            show_dev1 = False
            show_dev2 = False
            show_dev1_trend = True
            show_dev2_trend = True
        elif time_series_radio == "dev1_dev2_dev1trend_dev2trend":
            show_dev1 = True
            show_dev2 = True
            show_dev1_trend = True
            show_dev2_trend = True
        else:
            show_dev1 = None
            show_dev2 = None
            show_dev1_trend = None
            show_dev2_trend = None

        # title
        titleTimeSeries = st.text_input(
            "Title",
            value="Time series plot",
            key='titleTimeSeries',
            help="Change title of the time series plot",
        )
        # x label
        labelXTimeSeries = st.text_input(
            "Label x-axis",
            value="Time",
            key='labelXTimeSeries',
            help="Change label of the x-axis",
        )
        # y label
        labelYTimeSeries = st.text_input(
            "Label y-axis",
            value="Dev1 & Dev2",
            key='labelYTimeSeries',
            help="Change label of the y-axis",
        )

    with info_c, st.spinner(text="Preparing figure time series..."):
        fig_time_series = analysis.fig_time_series_plot(
            df=st.session_state.dfPreprocessing.copy(deep=True),
            x='Datetime',
            y1='Dev1',
            y2='Dev2',
            title_text=titleTimeSeries,
            group_color=groupBy,
            show_dev1 = show_dev1,
            show_dev2 = show_dev2,
            show_dev1_trend=show_dev1_trend,
            show_dev2_trend=show_dev2_trend,
            # entry_bp = 'EntryBP',
            window_size_trendline=window_size_trendline,
            xlabel=labelXTimeSeries,
            ylabel=labelYTimeSeries,
        )

        fileNameTimeSeries = str("TimeSeries" + "_" + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        ts_c.plotly_chart(figure_or_data=fig_time_series,
                          config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameTimeSeries,
                                                           'height': height,'width': width, 'scale': scale}})
