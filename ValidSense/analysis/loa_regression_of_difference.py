import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
# from pymer4.models import Lm


def loa_regression_of_difference(df: pd.DataFrame, bias_order: int = 0, loa_order: int = 0):
    """
    Function to calculate the bias and limits of agreement statistics according to the regression of difference
    limits of agreement analysis. This subtype corrects for systematic relationship between difference and mean, see
    https://pubmed.ncbi.nlm.nih.gov/10501650/ (section 3.2).
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param bias_order: (int = 0) order of equation for bias. 0 is horizontal bias, 1 is linear bias.
    :param loa_order: (int = 0) order of equation for limits of agreement. 0 is horizontal limits of agreement, 1 is
    linear limits of agreement.
    :return: ([pandas DataFrame, str, statsmodels.regression.linear_model.RegressionResultsWrapper,
    statsmodels.regression.linear_model.RegressionResultsWrapper]) dataframe with regression of
    difference limits of agreement analysis statistics, assumptions and model properties (when bias_order,
    respectively loa_order, is set to 1).
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(bias_order, int):
        raise TypeError(f"bias_order is of type {type(bias_order).__name__}, should be int")
    if not isinstance(loa_order, int):
        raise TypeError(f"loa_order is of type {type(loa_order).__name__}, should be int")
    if 'Diff' not in df.columns:
        raise KeyError("Diff not existing in df")
    if 'Mean' not in df.columns:
        raise KeyError("Mean not existing in df")
    if df['Diff'].isnull().values.any():
        raise ValueError("Diff contains missing values")
    if df['Mean'].isnull().values.any():
        raise ValueError("Mean contains missing values")

    assumptions = [
        True,  # Assumption 0: Normal distribution of the difference
        False, # Assumption 1: Constant agreement over the measurement range
        True,  # Assumption 2: Independent observations
        False, # Assumption 3: Within-cluster-SD independent of cluster-mean
        True,  # Assumption 4: Normal distribution of residuals
        True,  # Assumption 5: Homogeneity of residuals
        False, # Assumption 6: Exogeneity of fixed effects.
    ]

    try:
        df_bias_loa = pd.DataFrame(columns=['Bias', 'UpperLoA', 'LowerLoA'],
                               index=['Intercept', 'Slope'])  # empty 2x3 dataframe

        # variables (local)
        z = 1.96                    # z-score of the 95% estimated interval assuming a normal distribution of diff

        corr_hlf_nrm = np.sqrt(np.pi / 2)  # correction for half normal distribution

        # set mdl_bias and mdl_loa to None, will be overwritten when regression model is used
        mdl_bias = None  # no fitted and residual values
        mdl_loa = None  # no fitted and residual values

        # set parameters to None, will be overwritten if bias_order and loa_order is correctly inserted
        b0 = None
        b1 = None
        std = None
        std_order_0 = None
        std_order_1 = None
        g0 = None
        g1 = None

        # bias
        if bias_order == 0:
            b0 = np.mean(df['Diff'])
            b1 = 0
            df['AbsResiduals'] = abs(df['Diff'] - b0)       # deviation of diff around bias-->necessary for loa_order=1
            std = np.std(df['Diff'], ddof=1)                # deviation of diff around bias-->necessary for loa_order=0
            std_order_0 = std
        elif bias_order == 1:
            # linear model bias
            form_bias = str('Diff' + ' ~ ' + 'Mean')        # formula for linear model (dependent var ~ independent var)
            # mdl_bias = Lm(form_bias, data=df)               # linear model bias
            # mdl_bias.fit(summarize=False)                   # fit model, do not show
            # b0 = mdl_bias.coefs['Estimate']['Intercept']
            # b1 = mdl_bias.coefs['Estimate']['Mean']
            mdl_bias = smf.ols(form_bias, data=df).fit()    # linear model bias
            b0 = mdl_bias.params['Intercept']
            b1 = mdl_bias.params['Mean']

            # df['AbsResiduals'] = abs(mdl_bias.residuals)    # deviation of diff around bias-->necessary for loa_order=1
            df['AbsResiduals'] = abs(mdl_bias.resid)        # deviation of diff around bias-->necessary for loa_order=1
            std = np.std(mdl_bias.resid, ddof=2)            # deviation of diff around bias-->necessary for loa_order=0
            std_order_1 = std

        # 95% LoA
        if loa_order == 0:
            g0 = std * z
            g1 = 0
        elif loa_order == 1:
            # linear model loa
            form_loa = str(         # dependent var (absolute residuals of mdl_bias) and mean as independent var (mean)
                'AbsResiduals' + ' ~ ' + 'Mean')
            # mdl_loa = Lm(form_loa, data=df)
            # mdl_loa.fit(summarize=False)
            # g0 = mdl_loa.coefs['Estimate']['Intercept'] * z * corr_hlf_nrm
            # g1 = mdl_loa.coefs['Estimate']['Mean'] * z * corr_hlf_nrm
            mdl_loa = smf.ols(form_loa, data=df).fit()  # linear model 95% LoA
            g0 = mdl_loa.params['Intercept'] * z * corr_hlf_nrm
            g1 = mdl_loa.params['Mean'] * z * corr_hlf_nrm

        # drop AbsResiduals column
        df.drop(columns=['AbsResiduals'], inplace=True)

        # save in df_bias_loa
        df_bias_loa['Bias']['Intercept'] = b0
        df_bias_loa['UpperLoA']['Intercept'] = b0 + g0
        df_bias_loa['LowerLoA']['Intercept'] = b0 - g0
        df_bias_loa['Bias']['Slope'] = b1
        df_bias_loa['UpperLoA']['Slope'] = b1 + g1
        df_bias_loa['LowerLoA']['Slope'] = b1 - g1
        if std_order_0 is not None:
            df_bias_loa['SD'] = [std, None]
        if std_order_1 is not None:
            df_bias_loa['SD-residuals-bias-model'] = [std, None]

        return [df_bias_loa, assumptions, mdl_bias, mdl_loa]

    except Exception as e:
        return e
