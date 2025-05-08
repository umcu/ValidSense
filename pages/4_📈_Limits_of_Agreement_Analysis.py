import pandas as pd
import streamlit as st
import numpy as np
from ValidSense import analysis
import datetime

###################################################### STREAMLIT ######################################################
st.set_page_config(layout="wide", page_title="ValidSense toolbox - Static Analysis")
st.title("📈 Limits of Agreement Analysis")
# containers main body
info_c = st.container()                 # container for information
warn_c = st.container()                 # container for error
an_c = st.container()                   # container for analysis
vis_c = st.container()                  # container for visualisation
stat_c = st.container()                 # container for additional LoA analysis statistics
ass_c = st.container()                  # container for assumptions

# containers sidebar
info_cs = st.sidebar.container()        # container for information
an_cs = st.sidebar.container()          # container sidebar for analysis
stat_cs = st.sidebar.container()        # container sidebar for statistics
vis_cs = st.sidebar.container()         # container sidebar for visualisation
ass_show_cs = st.sidebar.container()    # container sidebar for assumptions show
ass_exp_cs = st.sidebar.container()     # container sidebar for assumptions expander

# session state between pages to save values, and save the inserted value.
for k, v in st.session_state.items():
    st.session_state[k] = v
# see https://discuss.streamlit.io/t/how-to-maintain-inputs-on-changing-endpoints/33474/7

# information
info_c.write(
    """
    Show the Bland-Altman plot based on the LoA analysis. **Check carefully all assumptions of the LoA analysis for 
    valid results!** Tools for assumption checking are provided in the sidebar.
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

########################################## DISPLAY DATAFRAME BEFORE ANALYSIS ###########################################
if an_cs.checkbox("Show dataset table"):
    an_c.header("Dataset table")
    an_c.dataframe(df)

############################################## CALCULATE BIAS AND 95% LOA ##############################################
std = None
modelBias = None
modelLoa = None
modelRep = None

# get bias and limits of agreement from different types of limits of agreement analysis
if loaSelect == 'Classic':
    with info_c, st.spinner(text="Calculating LoA analysis statistics..."):
        # get limits of agreement classic statistics and assumptions
        [dfBiasLoa, assumptions] = analysis.loa_classic(df=df)

elif loaSelect == 'Repeated measurements':
    with info_c, st.spinner(text="Calculating LoA analysis statistics..."):
        # get limits of agreement repeated measurements statistics and assumptions
        [dfBiasLoa, assumptions, modelRep] = analysis.loa_repeated_measurements(df=df, group_by=groupBy)

elif loaSelect == 'Regression of difference':
    with stat_cs.expander("**Regression of difference LoA analysis settings**"):
        # radio to determine fixed of flexible bias
        biasOptions = ['Constant bias', 'Non-constant bias']
        biasSel = st.radio(
            label="**Bias** over the measurement range is constant or non-constant:",
            options=biasOptions,
            key='biasSel',
            help="The bias can be constant or non-constant over the measurement range. **Constant** means no "
                 "systematic relationship between the _difference_ and _mean_. **Non-constant** means a linear "
                 "relationship between the _difference_ and _mean_.",
        )
        if biasSel == biasOptions[0]:
            biasOrder = 0
        elif biasSel == biasOptions[1]:
            biasOrder = 1

        # radio to determine limits of agreement order of equation
        loaOptions = ['Constant 95% LoA', 'Non-constant 95% LoA']
        loaSel = st.radio(
            label="**95% LoA** over the measurement range is constant or non-constant:",
            options=loaOptions,
            key='loaSel',
            help="The 95% LoA can be constant or non-constant over the measurement range. **Constant** means no "
                 "systematic relationship between the _difference_ and _mean_. **Non-constant** means a linear "
                 "relationship between the _difference_ and _mean_.",
        )
        if loaSel == loaOptions[0]:
            loaOrder = 0
        elif loaSel == loaOptions[1]:
            loaOrder = 1

    with info_c, st.spinner(text="Calculating LoA analysis statistics..."):
        # get limits of agreement regression of difference statistics and assumptions
        [dfBiasLoa, assumptions, modelBias, modelLoa] = analysis.loa_regression_of_difference(
            df=df,
            bias_order=biasOrder,
            loa_order=loaOrder
        )

elif loaSelect == 'Mixed-effect':
    with stat_cs.expander("**Mixed-effect LoA analysis settings**"):
        biasFixedVar = st.multiselect(
            label="Select fixed variables for bias model",
            options=df.columns,
            key='biasFixedVar',
            help="Fixed effects for bias."
        )

        # biasRandomVar = st.multiselect(
        #     label="Select random variables for bias model",
        #     options=df.columns,
        #     key='biasRandomVar',
        #     default=groupBy,
        #     help="Random effect for bias. Minimal one random effect is required, and default is cluster variable."
        # )

        loaFixedVar = st.multiselect(
            label="Select fixed variables for 95% LoA model",
            options=df.columns,
            key='loaFixedVar',
            help="Fixed effects for 95% LoA."
        )
        # loaRandomVar = st.multiselect(
        #     label="Select random variables for 95% LoA model",
        #     options=df.columns,
        #     key='loaRandomVar',
        #     default=groupBy,
        #     help="Random effect for 95% LoA. Minimal one random effect is required, and default is cluster variable."
        # )

    # # error if biasRandomVar is empty list
    # if len(biasRandomVar) == 0:
    #     warn_c.error("Select minimally one random variable for bias before continuing.")
    #     st.stop()

    # # error if loaRandomVar is empty list
    # if len(loaRandomVar) == 0:
    #     warn_c.error("Select minimally one random variable for 95% LoA before continuing.")
    #     st.stop()

    with info_c, st.spinner(text="Calculating LoA analysis statistics..."):
        # get limits of agreement Mixed-effect statistics and assumptions
        [dfBiasLoa, assumptions, modelBias, modelLoa] = analysis.loa_mixed_effect_model(
            df=df,
            bias_fixed_variable=biasFixedVar,
            bias_random_variable=[groupBy],
            loa_fixed_variable=loaFixedVar,
            loa_random_variable=[groupBy],
        )

else:
    dfBiasLoa = None
    dfBiasLoaTime = None
    assumptions = None

# dfBiasLoa, dfBiasLoaTime and assumptions to session_state
st.session_state.dfBiasLoa = dfBiasLoa.copy(deep=True)
st.session_state.assumptions = assumptions

# add fits and residuals to df if exist in locals and is not None   ##########################################################################
if 'modelBias' in locals() and modelBias != None:
    df = analysis.df_add_model_fits_residuals(df, modelBias, 'Bias')

if 'modelLoa' in locals() and modelLoa != None:
    df = analysis.df_add_model_fits_residuals(df, modelLoa, '95LoA')

################################################## BLAND-ALTMAN PLOT ###################################################
if vis_cs.checkbox(label="Show Bland-Altman plot", value=True):
    with vis_cs.expander("**Bland-Altman plot settings**"):
        # cluster
        groupColor = st.selectbox(
            label="Colour variable",
            options=[None] + df.columns.array.tolist(),
            key='groupColor',
            help="Colour a variable. For example, trends in the data might be identified by selecting the "
                 "cluster variable."
        )
        heatmap = st.checkbox(
            label="Heatmap",
            value=False,
            key='heatmap',
            help="Show the density of measurements in different regions to prevent overplotting in large datasets.",
        )
        # heatmap & marginal distribution plot
        if heatmap:
            nbins = st.number_input(
                label="Number of bins",
                min_value=0,
                key='nbins',
                help="The division of the data range into a fixed number of intervals, which are then represented by "
                     "the blue boxes. If _0_, the number of bins are automatically calculated.",
            )
            if nbins == 0:
                nbins = None
            marginal = None
        else:
            nbins = None
            marginal = st.selectbox(
                label="Marginal distribution subplot",
                options=[None, 'rug', 'box', 'violin', 'histogram'],
                key='marginal',
                help="Add marginal distribution subplots to the Bland-Altman plot for pattern recognition. More "
                     "information https://plotly.com/python-api-reference/generated/plotly.express.scatter.html."
            )
        # title
        titleBlandAltmanPlot = st.text_input(
            "Title",
            value="Bland-Altman plot",
            key='titleBlandAltmanPlot',
            help="Change title of the Bland-Altman plot",
        )
        # x label
        labelXBlandAltmanPlot = st.text_input(
            "Label x-axis",
            value="Mean",
            key='labelXBlandAltmanPlot',
            help="Change label of the x-axis",
        )
        # y label
        labelYBlandAltmanPlot = st.text_input(
            "Label y-axis",
            value="Difference",
            key='labelYBlandAltmanPlot',
            help="Change label of the y-axis",
        )
        # info
        st.write("The figure can be downloaded from the upper right corner of the figures (:camera:).")

        if st.checkbox(label="Show additional information about the LoA analysis"):
            stat_c.subheader("Additional information of the LoA analysis")
            stat_c.dataframe(dfBiasLoa)
            # information of modelBias and modelLoa
            if modelBias is not None:
                stat_c.write("**Model bias**")
                stat_c.write(modelBias.summary())
            if modelLoa is not None:
                stat_c.write("**Model 95% LoA**")
                stat_c.write(modelLoa.summary())
            if modelRep is not None:
                stat_c.write("**ANOVA model for Repeated Measurements**")
                stat_c.write(modelRep.anova_summary)

    # bland altman plot display
    with info_c, st.spinner(text="Preparing Bland-Altman plot..."):
        figBlandAltmanPlot = analysis.fig_bland_altman_plot(
            df=df,
            df_bias_loa=dfBiasLoa,
            x='Mean',
            y='Diff',
            title_text=titleBlandAltmanPlot,
            heatmap=heatmap,
            heatmap_nbins=nbins,
            marginal=marginal,
            xlabel=labelXBlandAltmanPlot,
            ylabel=labelYBlandAltmanPlot,
            group_color=groupColor,
        )
        vis_c.header("Bland-Altman plot")
        fileNameBlandAltmanPlot = str("BlandAltmanPlot" + "_" + loaSelect.replace(" ", "") +"_" +
                                     datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        vis_c.plotly_chart(figure_or_data=figBlandAltmanPlot,
                           config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameBlandAltmanPlot,
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
ass_show_cs.header("Tools for checking assumptions")
# Histogram
if test_histogram:
    if ass_show_cs.checkbox(label="Show histogram"):
        with ass_exp_cs.expander("**Histogram settings**"):
            # number of bins
            histNumberBins = st.number_input(
                label="Number of bins",
                min_value=0,
                max_value=len(df),
                value=0,
                key="histNumberBins",
                help="Number of bins of the histogram. Default (0) is automatic. More information: "
                     "https://plotly.github.io/plotly.py-docs/generated/plotly.expr"
                     "ess.histogram.html"
            )
            # column for histogram
            histColumn = st.selectbox(
                label="Select variable",
                options=df.columns,
                index=df.columns.get_loc('Diff'),
                key="histColumn",
                help="Variable to show the distribution of the values. More information: "
                     "https://plotly.github.io/plotly.py-docs/generated/plotly.express.histogram.html"
            )

            # error and stop if histColumn is not selected
            if histColumn is None:
                warn_c.error("Select a variable to visualise distribution in the histogram before continuing.")
                st.stop()

        # histogram
        with info_c, st.spinner(text="Preparing histogram..."):
            figHistogram = analysis.fig_histogram(
                df=df,
                column=histColumn,
                number_bins=histNumberBins,
            )

            fileNameHistogram = str("Histogram" + "_" + loaSelect.replace(" ", "") + "_" +
                                    datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figHistogram,
                               config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameHistogram,
                                                                'height': height, 'width': width, 'scale': scale}})

# Q-Q plot (default = 'Diff')
if test_qq_plot:
    if ass_show_cs.checkbox(label="Show Q-Q plot"):
        with ass_exp_cs.expander("**Q-Q plot settings**"):
            # column for qq-plot
            qqPlotColumn = st.selectbox(
                label="Select variable",
                options = df.columns,
                index=df.columns.get_loc('Diff'),
                key='qqPlotColumn',
                help="Variable to show the distribution of the values. More information: "
                     "https://www.statsmodels.org/dev/generated/statsmodels.graphics.gofplots.qqplot.html"
            )

            # reference line (default: 's')
            qqPlotLine = st.selectbox(
                label="Reference line",
                options=[None, '45', 's', 'r', 'q'],
                index=2,
                key='qqPlotLine',
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
            qqPlotFit = st.checkbox(
                label="Standardized data",
                value=True,
                key='qqPlotFit',
                help="The quantiles are formed from the standardized data, more information: "
                     "https://www.statsmodels.org/dev/generated/statsmodels.graphics.gofplots.qqplot.html"
            )

        # error and stop if qqPlotColumn is not selected
        if qqPlotColumn is None:
            warn_c.error("Select a variable to visualise distribution in the Q-Q plot before continuing.")
            st.stop()

        # qq-plot
        with info_c, st.spinner(text="Preparing Q-Q plot..."):
            figQQPlot = analysis.fig_qq_plot(
                df=df,
                column=qqPlotColumn,
                line=qqPlotLine,
                fit=qqPlotFit
            )
            fileNameQQplot = str("Q-Q plot" + "_" + loaSelect.replace(" ", "") + "_" +
                                 datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figQQPlot,
                               config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameQQplot,
                                                                'height': height, 'width': width, 'scale': scale}})

# Scatterplot
if test_scatterplot:
    if ass_show_cs.checkbox(label="Show scatterplot"):
        with ass_exp_cs.expander("**Scatterplot settings**"):
            scatterGroupColor = st.selectbox(
                label="Colour variable",
                options=[None] + df.columns.array.tolist(),
                index=0,
                key='scatterGroupColor',
                help="Colour a variable. For example, trends in the data might be identified by selecting the "
                     "cluster variable."
            )

            # marginal distribution plot
            marginalScatter = st.selectbox(
                label="Marginal distribution subplot",
                options=[None, 'rug', 'box', 'violin', 'histogram'],
                key='marginalScatter',
                help="Add marginal distribution subplots to the Bland-Altman plot for pattern recognition. More "
                     "information https://plotly.com/python-api-reference/generated/plotly.express.scatter.html."
            )
            # title
            titleScatterPlot = st.text_input(
                "Title",
                value="Scatterplot",
                key='titleScatterPlot',
                help="Change title of the scatterplot",
            )
            # x label
            labelXScatterPlot = st.text_input(
                "Label x-axis",
                value="Mean",
                key='labelXScatterPlot',
                help="Change label of the x-axis",
            )
            # y label
            labelYScatterPlot = st.text_input(
                "Label y-axis",
                value="Difference",
                key='labelYScatterPlot',
                help="Change label of the y-axis",
            )

        # Scatterplot
        with info_c, st.spinner(text="Preparing Scatterplot..."):
            figScatterPlot = analysis.fig_scatter_plot(
                df=df,
                x='Mean',
                y='Diff',
                title_text=str(titleScatterPlot),
                marginal=marginalScatter,
                xlabel=labelXScatterPlot,
                ylabel=labelYScatterPlot,
                group_color=scatterGroupColor,
            )

            fileNameScatterplot = str("Scatterplot" + "_" + loaSelect.replace(" ","") + "_" +
                                      datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figScatterPlot,
                               config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameScatterplot,
                                                                'height': height, 'width': width,'scale': scale}})

# Residual plot
if test_residualplot:
    if ass_show_cs.checkbox(label="Show residual plot"):
        with ass_exp_cs.expander("**Residual plot settings**"):
            # x-axis
            residualPlotX = st.selectbox(
                label="Fitted values of the model",
                options=df.columns.array.tolist(),
                index=df.columns.get_loc('model95LoAFittedValues'),
                key='residualPlotX',
                help="Fitted values of the model on the x-axis",
            )

            residualPlotY = st.selectbox(
                label="Residuals of the model",
                options=df.columns.array.tolist(),
                index=df.columns.get_loc('model95LoAResiduals'),
                key='residualPlotY',
                help="Residuals of the model on the y-axis",
            )

        # error and stop if residualPlotX or residualPlotY is not selected
        if residualPlotX is None or residualPlotY is None:
            warn_c.error("Select variables indicating fitted values and/or residuals for the residual plot "
                         "before continuing.")
            st.stop()

        # Residual plot
        with info_c, st.spinner(text="Preparing Residual plot..."):
            figResidualPlot = analysis.fig_residual_plot(
                df=df,
                fits=residualPlotX,
                residuals=residualPlotY
            )
            fileNameResidualPlot = str("Residual plot" + "_" + loaSelect.replace(" ","") + "_" +
                                       datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figResidualPlot,
                               config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameResidualPlot,
                                                                'height': height, 'width': width,'scale': scale}})

# Within-cluster-SD plot
if test_within_cluster_SD_plot:
    if ass_show_cs.checkbox(label="Show within-cluster-SD plot"):
        with ass_exp_cs.expander("**Within-cluster-SD plot settings**"):

            withinGroupStdPlotGroup = st.selectbox(
                label="Cluster variable",
                options=df.columns.array.tolist(),
                index=df.columns.get_loc(groupBy),
                key='withinGroupStdPlotGroup',
                help="Check the within-cluster standard deviation."
            )

        # error and stop if withinGroupStdPlotGroup is not selected
        if withinGroupStdPlotGroup is None:
            warn_c.error("Select the cluster variable in the within-cluster-SD plot before continuing.")
            st.stop()

        # Within-Group Std plot
        with info_c, st.spinner(text="Preparing Within-cluster-SD plot..."):
            figWithinGroupStdPlot = analysis.fig_within_group_std_plot(df=df, group=withinGroupStdPlotGroup)

            fileNameWithinGroupStdPlot = str("Within-cluster-SD plot" + "_" + loaSelect.replace(" ","") + "_" +
                                             datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            ass_c.plotly_chart(figure_or_data=figWithinGroupStdPlot,
                               config={'toImageButtonOptions': {'format': 'png', 'filename': fileNameWithinGroupStdPlot,
                                                                'height': height,'width': width, 'scale': scale}})

# Covariance
if test_covariance:
    if ass_show_cs.checkbox(label="Show covariance"):
        with ass_exp_cs.expander("**Covariance settings**"):
            covX = st.selectbox(
                label="Fixed effect variable",
                options=[None] + df.columns.array.tolist(),
                index=0,
                key="covX",
                help="Measure the relationship between variables by the covariance."
            )
            covY = st.selectbox(
                label="Select random effect or residual variable",
                options=[None] + df.columns.array.tolist(),
                index=0,
                key='covY',
            )

        # error and stop if covX or covY is not selected
        if covX is None or covY is None:
            warn_c.error("Select the variables for covariance before continuing.")
            st.stop()
        with info_c, st.spinner(text="Preparing Covariance calculation..."):
            covariance = np.cov(df[covX], df[covY])[0][1]
            covariance_round = round(covariance, 2)
            ass_c.write(f"**Covariance** between _{covX}_ and _{covY}_: **{covariance_round}**")





