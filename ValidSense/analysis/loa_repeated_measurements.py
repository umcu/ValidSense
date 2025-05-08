import pandas as pd
import numpy as np
from bioinfokit.analys import stat

def loa_repeated_measurements(df: pd.DataFrame, group_by: str = 'Sub'):

    """
    Function to calculate the bias and limits of agreement statistics according to the repeated measurements (multiple
    observations per subject) limits of agreement analysis. This subtype corrects for multiple observations per
    subject, see https://pubmed.ncbi.nlm.nih.gov/10501650/ (section 5.2) and https://pubmed.ncbi.nlm.nih.gov/17613642/
    (section 3).
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param group_by: (str= 'Sub') column in dataframe where multiple subjects are grouped by.
    :return: ([pandas DataFrame, str, bioinfokit analys stat]) dataframe with repeated (multiple observations per
    subject) limits of agreement analysis statistics, assumptions and model.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(group_by, str):
        raise TypeError(f"group_by is of type {type(group_by).__name__}, should be str")
    if 'Diff' not in df.columns:
        raise KeyError("Diff not existing in df")
    if 'Mean' not in df.columns:
        raise KeyError("Mean not existing in df")
    if group_by not in df.columns:
        raise KeyError("group_by not existing in df.")
    if df['Diff'].isnull().values.any():
        raise ValueError("Diff contains missing values")
    if df['Mean'].isnull().values.any():
        raise ValueError("Mean contains missing values")
    if df[group_by].isnull().values.any():
        raise ValueError("group_by contains missing values")

    assumptions = [
        True,  # Assumption 0: Normal distribution of the difference
        True,  # Assumption 1: Constant agreement over the measurement range
        False, # Assumption 2: Independent observations
        True,  # Assumption 3: Within-cluster-SD independent of cluster-mean
        False, # Assumption 4: Normal distribution of residuals
        False, # Assumption 5: Homogeneity of residuals
        False, # Assumption 6: Exogeneity of fixed effects.
    ]

    # set mdl to None, overwrite later if used
    mdl = None
    df_summary_rep = None

    try:
        df_bias_loa = pd.DataFrame(columns=['Bias', 'UpperLoA', 'LowerLoA'], index=['Intercept'])  # empty 1x3 dataframe
        df[group_by] = df[group_by].astype(str)  # set groupby column to str, to prevent LinAlgError("SVD did not converge")

        # check if group_by in df consist of at least one group
        unique_in_group_by = df[group_by].nunique()  # number of unique values
        if unique_in_group_by < 2:
            df_bias_loa['Bias']['Intercept'] = np.nan
            df_bias_loa['UpperLoA']['Intercept'] = np.nan
            df_bias_loa['LowerLoA']['Intercept'] = np.nan
            print(
                "Warning: Statistics of the Repeated Measurements can not be calculated. More than one subject should "
                "be included in group_by. Number of unique subjects in group_by: " + str(unique_in_group_by))
        # check if number of rows is more than number of groups, otherwise we divide by 0 and receive an error
        elif unique_in_group_by >= len(df):
            df_bias_loa['Bias']['Intercept'] = np.nan
            df_bias_loa['UpperLoA']['Intercept'] = np.nan
            df_bias_loa['LowerLoA']['Intercept'] = np.nan
            print(
                "Warning: Statistics of the Repeated Measurements can not be calculated. More items per group should"
                " be included in the data. len(df) should be larger than the number of groups.")
        else:
            # variables (local)
            z = 1.96  # z-score of the 95% estimated interval assuming a normal distribution of diff

            # bias
            b0 = np.mean(df['Diff'])

            # limits of agreement
            mdl = stat()  # empty results anova
            formula = str('Diff' + ' ~ C(' + group_by + ')')  # dependent var ~ independent var
            mdl.anova_stat(df=df, res_var='diff', anova_model=formula)  # results one-way ANOVA
            # MS_Sub = res.anova_summary['mean_sq']['C(Sub)']           # mean square subject
            MS_Sub = mdl.anova_summary['mean_sq'][str('C(' +
                                                      group_by + ')')]  # mean square subject
            MS_Res = mdl.anova_summary['mean_sq']['Residual']  # mean square residual
            obs_group = df.groupby([group_by])[group_by].count()  # observations per group (sub)
            obs_group_sq = sum(np.square(  # observation per group squared (sum(m^2,i)
                df.groupby([group_by])[group_by].count()))
            obs_sub = obs_group.count()  # number of subjects
            obs_tot = df[group_by].count()  # total number of observations
            div = (np.square(obs_tot) - obs_group_sq) / \
                  ((obs_sub - 1) * obs_tot)  # divisor to corrected for heterogeneity
            var_within_sub = MS_Res  # within subject variance
            var_between_sub = (MS_Sub - MS_Res) / div  # between subject variance
            std = np.sqrt((MS_Sub - MS_Res) / div + MS_Res)  # std corrected for repeated measurements
            g0 = std * z

            # save in df_bias_loa
            df_bias_loa['Bias']['Intercept'] = b0
            df_bias_loa['UpperLoA']['Intercept'] = b0 + g0
            df_bias_loa['LowerLoA']['Intercept'] = b0 - g0
            df_bias_loa['Between-'+group_by+'-var'] = var_between_sub
            df_bias_loa['Within-'+group_by+'-var'] = var_within_sub
            df_bias_loa['Between-'+group_by+'-std'] = np.sqrt(var_between_sub)
            df_bias_loa['Within-'+group_by+'-std'] = np.sqrt(var_within_sub)
            df_bias_loa['Total-std'] = std

        return [df_bias_loa, assumptions, mdl]

    except Exception as e:
        print(e)
        return e
