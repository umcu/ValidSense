import plotly.express as px
import pandas as pd

# variables
size_plot = [700, 500]  # width, height
marginal = None         # [None, 'rug', 'box', 'violin']
size_marker = 5  # marker size
size_title = 30
size_label = 25
size_tick = 25
color_marker = px.colors.qualitative.Plotly


def fig_residual_plot(df: pd.DataFrame, fits: str, residuals: str):
    """
    Function to create residual plot, with fitted values on the x-axis, residuals on the y-axis.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param fits: (str) fitted values of the regression model or mixed effect model
    :param residuals: (str) residuals of the regression model or mixed effect model
    :return: (plotly.graph_objs._figure.Figure) Residual plot with ordinary least squares trendline.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(fits, str):
        raise TypeError(f"fits is of type {type(fits).__name__}, should be str")
    if not isinstance(residuals, str):
        raise TypeError(f"residuals is of type {type(residuals).__name__}, should be str")
    if fits not in df.columns:
        raise KeyError("fits not existing in df")
    if residuals not in df.columns:
        raise KeyError("residuals not existing in df")

    try:
        title = str("Residual plot of " + str(residuals))

        fig = px.scatter(data_frame=df,
                         x=fits,
                         y=residuals,
                         width=size_plot[0],
                         height=size_plot[1],
                         title=title,
                         marginal_x=marginal,  # marginal distribution
                         marginal_y=marginal,
                         trendline='ols',       # ordinary least squares
                         trendline_color_override="red",
                         hover_data=df.columns,
                         color_discrete_sequence=color_marker,
                         )

        # change size
        fig.update_traces(marker={'size': size_marker})
        fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_layout(title_font_size=size_title)

        return fig

    except Exception as e:
        return e

# https://plotly.com/python/ml-regression/
