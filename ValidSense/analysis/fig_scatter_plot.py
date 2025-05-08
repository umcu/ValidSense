import plotly.express as px
import pandas as pd
import numpy as np

# variables
size_plot = [700, 500]  # width, height
space = [0.05, 0.05]  # additional spacing in fractions: [x_axis_range, y_axis_range]
size_marker = 10  # marker size
size_title = 30
size_label = 25
size_tick = 25
color_marker = px.colors.qualitative.Plotly

def fig_scatter_plot(df: pd.DataFrame, x: str = 'Mean', y: str = 'Diff', group_color: str = None,
                     title_text: str = 'Bland-Altman plot', marginal: str = None, xlabel: str = 'Mean',
                     ylabel: str = 'Difference'):
    """
    Function to create a scatter plot.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param x: (str) x-axis
    :param y: (str) y-axis
    :param group_color: (str = None) column in df to group data by.
    :param title_text: (str = 'Bland-Altman plot') title of the difference plot.
    :param marginal (str = None) marginal subplots of horizontal and vertical axis if heatmap is False.
    :param xlabel (str = 'Mean') x label.
    :param ylabel (str = 'Difference') y label.
    :return: (plotly.graph_objs._figure.Figure) Scatter plot figure.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(x, str):
        raise TypeError(f"x is of type {type(x).__name__}, should be str")
    if not isinstance(y, str):
        raise TypeError(f"y is of type {type(y).__name__}, should be str")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel is of type {type(xlabel).__name__}, should be str")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel is of type {type(ylabel).__name__}, should be str")
    if not isinstance(group_color, (str, type(None))):
        raise TypeError(f"group_color is of type {type(group_color).__name__}, should be str or NoneType")
    if not isinstance(marginal, (str, type(None))):
        raise TypeError(f"marginal is of type {type(marginal).__name__}, should be str or NoneType")
    if x not in df.columns:
        raise KeyError("x not existing in df")
    if y not in df.columns:
        raise KeyError("y not existing in df")
    if group_color is not None and group_color not in df.columns:
        raise KeyError("group_color not existing in df")
    if marginal not in [None, 'rug', 'box', 'violin', 'histogram']:
        raise ValueError("marginal is of not None, 'rug', 'box', 'violin' or 'histogram'")

    try:
        # group_color should be column of df
        if group_color is not None:
            # sort by group_color
            df.sort_values(by=[group_color], ascending=True, inplace=True)

        fig = px.scatter(
            data_frame=df,
            x=x,
            y=y,
            hover_data=df.columns,
            color=group_color,
            color_discrete_sequence=color_marker,
            trendline='ols',  # ordinary least squares
            trendline_color_override="red",
            marginal_x=marginal,  # marginal distribution
            marginal_y=marginal,
        )

        # range of x-axis and y-axis
        x_axis_range = [int(np.floor(np.amin(df[x]))), int(np.ceil(np.amax(df[x])))]
        y_axis_range = [int(np.floor(np.amin(df[y]))), int(np.ceil(np.amax(df[y])))]

        # define and add spacing related to range
        x_axis_space = (x_axis_range[1] - x_axis_range[0]) * space[0]
        y_axis_space = (y_axis_range[1] - y_axis_range[0]) * space[1]
        x_axis_range_adapt = [x_axis_range[0] - x_axis_space, x_axis_range[1] + x_axis_space]
        y_axis_range_adapt = [y_axis_range[0] - y_axis_space, y_axis_range[1] + y_axis_space]

        # update range of x_axis and y_axis
        fig.update_xaxes(range=x_axis_range_adapt, row=1, col=1)
        fig.update_yaxes(range=y_axis_range_adapt, row=1, col=1)

        # change size, title, x_axis, y_axis

        fig.update_layout(
            width=size_plot[0],
            height=size_plot[1],
            title_text=title_text,
            title_font_size=size_title,
            xaxis_title=xlabel,
            yaxis_title=ylabel,
        )

        # change size
        fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)

        # # range of x-axis and y-axis
        # x_axis_range = [int(np.floor(np.amin(df[x]))), int(np.ceil(np.amax(df[x])))]
        # y_axis_range = [int(np.floor(np.amin(df[y]))), int(np.ceil(np.amax(df[y])))]
        #
        # # define and add spacing related to range
        # x_axis_space = (x_axis_range[1] - x_axis_range[0]) * space[0]
        # y_axis_space = (y_axis_range[1] - y_axis_range[0]) * space[1]
        # x_axis_range_adapt = [x_axis_range[0] - x_axis_space, x_axis_range[1] + x_axis_space]
        # y_axis_range_adapt = [y_axis_range[0] - y_axis_space, y_axis_range[1] + y_axis_space]
        #
        # # update range of x_axis and y_axis
        # fig.update_xaxes(range=x_axis_range_adapt, row=1, col=1)
        # fig.update_yaxes(range=y_axis_range_adapt, row=1, col=1)
        #
        # fig.update_layout(
        #     width=size_plot[0],
        #     height=size_plot[1],
        #     title_text="Scatterplot",
        #     # title_text="Scatter plot of BP change levels CPC measurements (mixed effect model)",
        #     xaxis_title=xlabel,
        #     yaxis_title=ylabel,
        # )
        #
        # # change size of markers
        # fig.update_traces(marker={'size': size_marker})
        #
        # # change size
        # fig.update_traces(marker={'size': size_marker})
        # fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        # fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)
        # fig.update_layout(title_font_size=size_title)

        return fig

    except Exception as e:
        return e

# https://plotly.com/python-api-reference/generated/plotly.express.scatter.html
