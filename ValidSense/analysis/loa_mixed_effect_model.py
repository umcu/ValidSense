import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
#
def loa_mixed_effect_model(df: pd.DataFrame, bias_fixed_variable: list, bias_random_variable: list,
                           loa_fixed_variable: list, loa_random_variable: list):
    """
    Function to calculate the bias, limits of agreement and standard deviation statistics according to the mixed effect
    model limits of agreement analysis. This subtype corrects for different fixed and random effects in both bias and
    limits of agreement, see https://pubmed.ncbi.nlm.nih.gov/27973556/.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param bias_fixed_variable: (list) list with fixed effects for bias.
    :param bias_random_variable: (list) list with random effects for bias.
    :param loa_fixed_variable: (list) list with fixed effects for loa.
    :param loa_random_variable: (list) list with random effects for loa.
    :return: ([pandas DataFrame, str, statsmodels.regression.mixed_linear_model.MixedLMResultsWrapper,
    statsmodels.regression.mixed_linear_model.MixedLMResultsWrapper]) dataframe with mixed effect model limits of
    agreement analysis statistics, their assumptions, and model properties of bias and 95% LoA.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(bias_fixed_variable, list):
        raise TypeError(f"bias_fixed_variable is of type {type(bias_fixed_variable).__name__}, should be list")
    if not isinstance(bias_random_variable, list):
        raise TypeError(f"bias_random_variable is of type {type(bias_random_variable).__name__}, should be list")
    if not isinstance(loa_fixed_variable, list):
        raise TypeError(f"loa_fixed_variable is of type {type(loa_fixed_variable).__name__}, should be list")
    if not isinstance(loa_random_variable, list):
        raise TypeError(f"loa_random_variable is of type {type(loa_random_variable).__name__}, should be list")
    if 'Diff' not in df.columns:
        raise KeyError("Diff not existing in df")
    if 'Mean' not in df.columns:
        raise KeyError("Mean not existing in df")
    if df['Diff'].isnull().values.any():
        raise ValueError("Diff contains missing values")
    if df['Mean'].isnull().values.any():
        raise ValueError("Mean contains missing values")
    if len(bias_random_variable) == 0:
        raise Exception("bias_random_variable is empty, minimal 1 random effect for bias should be included")
    if len(loa_random_variable) == 0:
        raise Exception("loa_random_variable is empty, minimal 1 random effect for bias should be included")

    assumptions = [
        True,  # Assumption 0: Normal distribution of the difference
        True,  # Assumption 1: Constant agreement over the measurement range
        False,  # Assumption 2: Independent observations
        True,  # Assumption 3: Within-cluster-SD independent of cluster-mean
        True,  # Assumption 4: Normal distribution of residuals
        True,  # Assumption 5: Homogeneity of residuals
        True,  # Assumption 6: Exogeneity of fixed effects.
    ]

    try:
        mdl_bias_fit = None
        mdl_loa_fit = None

        df_bias_loa = pd.DataFrame(columns=['Bias', 'UpperLoA', 'LowerLoA'], index=['Intercept'])  # empty 1x3 dataframe

        # check if bias_random_variable and loa_random_variable in df consist of at least one group
        unique_in_bias_random_variable = df[
            bias_random_variable].nunique().min()  # number of unique values, minimal, bias
        unique_in_loa_random_variable = df[loa_random_variable].nunique().min()  # number of unique values, minimal, loa
        if unique_in_bias_random_variable < 2 or unique_in_loa_random_variable < 2:
            # output to nan
            df_bias_loa['Bias']['Intercept'] = np.nan
            df_bias_loa['UpperLoA']['Intercept'] = np.nan
            df_bias_loa['LowerLoA']['Intercept'] = np.nan
            df_bias_loa['Within-std'] = np.nan
            df_bias_loa['Between-Obs-std'] = np.nan
            df_bias_loa['Total-Obs-std'] = np.nan
            mdl_bias = np.nan
            mdl_loa = np.nan
            warnings.warn("Statistics of the Mixed Effect Model can not be calculated. More than one subject should "
                "be included in bias_random_variable and loa_random_variable. Number of unique subjects in "
                "bias_random_variable: " + str(unique_in_bias_random_variable) + " and in loa_random_variable: " +
                str(unique_in_loa_random_variable))
            # print(
            #     "Warning: Statistics of the Mixed Effect Model can not be calculated. More than one subject should "
            #     "be included in bias_random_variable and loa_random_variable. Number of unique subjects in "
            #     "bias_random_variable: " + str(unique_in_bias_random_variable) + " and in loa_random_variable: " +
            #     str(unique_in_loa_random_variable))
        # check if number of rows is more than number of bias_random_variable or loa_random_variable, otherwise we
        # divide by 0 and receive an error
        elif unique_in_bias_random_variable >= len(df) or unique_in_loa_random_variable >= len(df):
            # output to nan
            df_bias_loa['Bias']['Intercept'] = np.nan
            df_bias_loa['UpperLoA']['Intercept'] = np.nan
            df_bias_loa['LowerLoA']['Intercept'] = np.nan
            df_bias_loa['Within-std'] = np.nan
            df_bias_loa['Between-Obs-std'] = np.nan
            df_bias_loa['Total-Obs-std'] = np.nan
            mdl_bias = np.nan
            mdl_loa = np.nan
            warnings.warn("Statistics of the Mixed Effect Model can not be calculated. More items per group should"
                " be included in the data. len(df) should be larger than the bias_random_variable or "
                "loa_random_variable")
            # print(
            #     "Warning: Statistics of the Mixed Effect Model can not be calculated. More items per group should"
            #     " be included in the data. len(df) should be larger than the bias_random_variable or "
            #     "loa_random_variable")
        else:
            # variables (local)
            z = 1.96  # z-score of the 95% estimated interval assuming a normal distribution of diff

            # formula bias
            formula_bias = 'Diff ~ 1 '      # general intercept
            for fix in bias_fixed_variable:
                formula_bias += '+' + fix

            # formula 95% LoA
            formula_loa = 'Diff ~ 1 '       # general intercept
            for rand in loa_fixed_variable:
                formula_loa += '+' + rand

            # model bias  ############################################################################################################################
            mdl_bias = smf.mixedlm(formula_bias, df, groups=df[bias_random_variable[0]])
            mdl_bias_fit = mdl_bias.fit()
            b0 = mdl_bias_fit.params['Intercept']

            # model 95% LoA
            mdl_loa = smf.mixedlm(formula_loa, df, groups=df[loa_random_variable[0]])
            mdl_loa_fit = mdl_loa.fit()
            var_list = [mdl_loa_fit.scale]                          # within-group-variance
            std_list = [np.sqrt(var_list[0])]
            name_list = ['Within-' + bias_random_variable[0] + '-SD']

            var_list.append(mdl_loa_fit.cov_re['Group']['Group'])   # between-group-variance
            std_list.append(np.sqrt(mdl_loa_fit.cov_re)['Group']['Group'])
            name_list.append('Between-' + bias_random_variable[0] + '-SD')

            std_tot = np.sqrt(sum(var_list))                # total std (first sum variance, then sqrt to get SD)
            std_list.append(std_tot)
            name_list.append('Total-SD')
            g0 = std_tot * z

            # save in df_bias_loa
            df_bias_loa['Bias']['Intercept'] = b0
            df_bias_loa['UpperLoA']['Intercept'] = b0 + g0
            df_bias_loa['LowerLoA']['Intercept'] = b0 - g0

            # append standard deviation to df_bias_loa
            for name in name_list:
                df_bias_loa[name] = std_list[name_list.index(name)]

        return [df_bias_loa, assumptions, mdl_bias_fit, mdl_loa_fit]

    except Exception as e:
        print(type(e))
        print(e)
        if type(e) is AttributeError:
            raise TypeError(
                "Potential reason for the TypeError could be that there is time included in the dataset, that "
                "is not converted to datetime in the preprocessing stage. Make sure that time is included, or "
                "manually remove this column from the dataset. Original warning: " + str(e))
        else:
            return e


# OLD, USES RPY2 PACKAGE, THAT CANNOT BE USED WHEN UPLOADING TO STREAMLIT OR POSTIT CONNECT
# import numpy as np
# import pandas as pd
# from rpy2.robjects.packages import importr
#
# importr("palettetown")  # needs "install.packages('palettetown') in R console beforehand
# importr("lmerTest")  # needs "install.packages('lmerTest') in R console beforehand
# from pymer4.models import Lmer
#
#
# # source:
# # http://eshinjolly.com/pymer4/_modules/pymer4/models/Lmer.html
#
# def loa_mixed_effect_model(df: pd.DataFrame, bias_fixed_variable: list, bias_random_variable: list,
#                           loa_fixed_variable: list, loa_random_variable: list):
#     """
#     Function to calculate the bias, limits of agreement and standard deviation statistics according to the mixed effect
#     model limits of agreement analysis. This subtype corrects for different fixed and random effects in both bias and
#     limits of agreement, see https://pubmed.ncbi.nlm.nih.gov/27973556/.
#     :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
#     :param bias_fixed_variable: (list) list with fixed effects for bias.
#     :param bias_random_variable: (list) list with random effects for bias.
#     :param loa_fixed_variable: (list) list with fixed effects for loa.
#     :param loa_random_variable: (list) list with random effects for loa.
#     :return: ([pandas DataFrame, str, pymer4.models.Lmer, pymer4.models.Lmer]) dataframe with mixed effect
#     model limits of agreement analysis statistics, their assumptions, and model properties of bias and limits of
#     agreement.
#     """
#
#     # warning
#     if not isinstance(df, pd.DataFrame):
#         raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
#     if not isinstance(bias_fixed_variable, list):
#         raise TypeError(f"bias_fixed_variable is of type {type(bias_fixed_variable).__name__}, should be list")
#     if not isinstance(bias_random_variable, list):
#         raise TypeError(f"bias_random_variable is of type {type(bias_random_variable).__name__}, should be list")
#     if not isinstance(loa_fixed_variable, list):
#         raise TypeError(f"loa_fixed_variable is of type {type(loa_fixed_variable).__name__}, should be list")
#     if not isinstance(loa_random_variable, list):
#         raise TypeError(f"loa_random_variable is of type {type(loa_random_variable).__name__}, should be list")
#     if 'Diff' not in df.columns:
#         raise KeyError("Diff not existing in df")
#     if 'Mean' not in df.columns:
#         raise KeyError("Mean not existing in df")
#     if df['Diff'].isnull().values.any():
#         raise ValueError("Diff contains missing values")
#     if df['Mean'].isnull().values.any():
#         raise ValueError("Mean contains missing values")
#     if len(bias_random_variable) == 0:
#         raise Exception("bias_random_variable is empty, minimal 1 random effect for bias should be included")
#     if len(loa_random_variable) == 0:
#         raise Exception("loa_random_variable is empty, minimal 1 random effect for bias should be included")
#
#     assumptions = [
#         True,  # Assumption 0: Normal distribution of the difference
#         True, # Assumption 1: Constant agreement over the measurement range
#         False,  # Assumption 2: Independent observations
#         True, # Assumption 3: Within-cluster-SD independent of cluster-mean
#         True,  # Assumption 4: Normal distribution of residuals
#         True,  # Assumption 5: Homogeneity of residuals
#         True, # Assumption 6: Exogeneity of fixed effects.
#     ]
#
#     try:
#         df_bias_loa = pd.DataFrame(columns=['Bias', 'UpperLoA', 'LowerLoA'], index=['Intercept'])  # empty 1x3 dataframe
#
#         # check if bias_random_variable and loa_random_variable in df consist of at least one group
#         unique_in_bias_random_variable = df[bias_random_variable].nunique().min()  # number of unique values, minimal, bias
#         unique_in_loa_random_variable = df[loa_random_variable].nunique().min()  # number of unique values, minimal, loa
#         if unique_in_bias_random_variable < 2 or unique_in_loa_random_variable <2:
#             # output to nan
#             df_bias_loa['Bias']['Intercept'] = np.nan
#             df_bias_loa['UpperLoA']['Intercept'] = np.nan
#             df_bias_loa['LowerLoA']['Intercept'] = np.nan
#             df_bias_loa['Within-std'] = np.nan
#             df_bias_loa['Between-Obs-std'] = np.nan
#             df_bias_loa['Total-Obs-std'] = np.nan
#             mdl_bias = np.nan
#             mdl_loa = np.nan
#             print(
#                 "Warning: Statistics of the Mixed Effect Model can not be calculated. More than one subject should "
#                 "be included in bias_random_variable and loa_random_variable. Number of unique subjects in "
#                 "bias_random_variable: " + str(unique_in_bias_random_variable) + " and in loa_random_variable: " +
#                 str(unique_in_loa_random_variable))
#         # check if number of rows is more than number of bias_random_variable or loa_random_variable, otherwise we
#         # divide by 0 and receive an error
#         elif unique_in_bias_random_variable >= len(df) or unique_in_loa_random_variable >= len(df):
#             # output to nan
#             df_bias_loa['Bias']['Intercept'] = np.nan
#             df_bias_loa['UpperLoA']['Intercept'] = np.nan
#             df_bias_loa['LowerLoA']['Intercept'] = np.nan
#             df_bias_loa['Within-std'] = np.nan
#             df_bias_loa['Between-Obs-std'] = np.nan
#             df_bias_loa['Total-Obs-std'] = np.nan
#             mdl_bias = np.nan
#             mdl_loa = np.nan
#             print(
#                 "Warning: Statistics of the Mixed Effect Model can not be calculated. More items per group should"
#                 " be included in the data. len(df) should be larger than the bias_random_variable or "
#                 "loa_random_variable")
#         else:
#             # variables (local)
#             z = 1.96  # z-score of the 95% estimated interval assuming a normal distribution of diff
#
#             # formula bias
#             if len(bias_fixed_variable) == 0:                       # include general intercept
#                 formula_bias = 'Diff ~ 1 + '
#             else:
#                 formula_bias = 'Diff ~ '
#                 for fix in bias_fixed_variable:
#                     formula_bias += fix + ' + '
#             for rand in bias_random_variable[:-1]:                  # all iterations expect last one
#                 formula_bias += '(1|' + rand + ') + '               # 1 is random intercept
#             formula_bias += '(1|' + bias_random_variable[0] + ')'
#
#             # formula loa
#             if len(loa_fixed_variable) == 0:                        # include general intercept
#                 formula_loa = 'Diff ~ 1 + '
#             else:
#                 formula_loa = 'Diff ~ '
#                 for fix in loa_fixed_variable:
#                     formula_loa += fix + ' + '
#             for rand in loa_random_variable[:-1]:                   # all iterations expect last one
#                 formula_loa += '(1|' + rand + ') + '                # 1 is random intercept
#             formula_loa += '(1|' + loa_random_variable[-1] + ')'
#
#             # model bias
#             mdl_bias = Lmer(formula=formula_bias, data=df)          # model for mean (without fixed effects)
#             mdl_bias.fit(summarize=False)
#             b0 = mdl_bias.coefs['Estimate']['(Intercept)']
#
#             # model limits of agreement
#             mdl_loa = Lmer(formula_loa, data=df)                    # main model for standard deviation
#             mdl_loa.fit(summarize=True)
#             var_list = [mdl_loa.ranef_var['Var']['Residual']]       # list with variance (start with within-patient var)
#             std_list = [mdl_loa.ranef_var['Std']['Residual']]       # list with std
#             name_list = ['Within-std']
#             for ran in loa_random_variable:
#                 name_list.append(str('Between-'+ran+'-std'))        # name of ran
#                 var_list.append(mdl_loa.ranef_var['Var'][ran])      # add between patient (+ other groups) variance to list
#                 std_list.append(mdl_loa.ranef_var['Std'][ran])      # similar for std
#             std_tot = np.sqrt(sum(var_list))                        # total std (first sum variance, then sqrt to get std)
#             std_list.append(std_tot)
#             name_list.append('Total-std')
#
#             g0 = std_tot * z
#
#             # save in df_bias_loa
#             df_bias_loa['Bias']['Intercept'] = b0
#             df_bias_loa['UpperLoA']['Intercept'] = b0 + g0
#             df_bias_loa['LowerLoA']['Intercept'] = b0 - g0
#
#             # append standard deviation to stat_df
#             for name in name_list:
#                 df_bias_loa[name] = std_list[name_list.index(name)]
#
#         return [df_bias_loa, assumptions, mdl_bias, mdl_loa]
#
#     except Exception as e:
#         print(type(e))
#         print(e)
#         if type(e) is AttributeError:
#             raise TypeError("Potential reason for the TypeError could be that there is time included in the dataset, that "
#                             "is not converted to datetime in the preprocessing stage. Make sure that time is included, or "
#                             "manually remove this column from the dataset. Original warning: " + str(e))
#         else:
#             return e
