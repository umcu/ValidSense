import pandas as pd
import statsmodels.api as sm


def df_add_model_fits_residuals(df: pd.DataFrame, model: sm.regression.mixed_linear_model.MixedLMResultsWrapper,
                                name: str):
    """
    Function to add model fits and residuals as column to df, with 'name' added in columnname.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param model: (statsmodels.regression.mixed_linear_model.MixedLMResultsWrapper) Statsmodel.
    :param name: (str) name of the model.
    :return: (pandas DataFrame) dataframe with added fits and regression columns.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(name, str):
        raise TypeError(f"name is of type {type(name).__name__}, should be str")
    if model is None:
        raise KeyError("model should not be None")

    try:
        # add column with name 'model{name}FittedValues' to df, representing the fitted value of the model
        df[f"model{name}FittedValues"] = model.fittedvalues
        # add column with name 'model{name}Residuals' to df, representing the residuals of the model
        df[f"model{name}Residuals"] = model.resid
        return df

    except Exception as e:
        return e
