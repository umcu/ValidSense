import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# variables
height_text = 30            # height of text above line
size_plot = [1200, 700]     # [width, height]
space = [0.05, 0.05]        # additional spacing in fractions: [x_axis_range, y_axis_range]
space_loc_an = 0.015          # additional spacing for annotation text in fraction of x_axis_range
color_marker = px.colors.qualitative.Plotly
color_line_bias = px.colors.qualitative.Plotly[0]
color_line_loa = px.colors.qualitative.Plotly[1]
color_line_zero = px.colors.sequential.Greys[4]  # categorical grey from white [0] to black [8]
color_density_heatmap = px.colors.sequential.Blues
color_density_heatmap[0] = 'rgba(255, 255, 255, 0)'  # change opacity (alpha) of white to zero
line_dash_bias = 'solid'    # dash of trace lines [‘solid’, ‘dot’, ‘dash’, ‘longdash’, ‘dashdot’, ‘longdashdot’]
line_dash_loa = 'dot'       # dash of trace lines [‘solid’, ‘dot’, ‘dash’, ‘longdash’, ‘dashdot’, ‘longdashdot’]
line_dash_zero = 'solid'
size_line_text = 20 # bias and 95% LoA
size_marker = 10  # marker size
size_title = 30
size_label = 25
size_tick = 25

def fig_bland_altman_plot(df: pd.DataFrame, df_bias_loa: pd.DataFrame, x: str = 'Mean', y: str = 'Diff',
                     group_color: str = None, title_text: str = 'Bland-Altman plot', heatmap: bool = False,
                     heatmap_nbins: int = None, marginal: str = None, xlabel: str = 'Mean', ylabel: str = 'Difference'):
    """
    Function to make the Bland-Altman plot, based on the statistics in df or df_bias_loa.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param df_bias_loa: (pandas DataFrame) dataframe with bias and limits of agreement statistics.
    :param x: (str = 'Mean') x-axis.
    :param y: (str = 'Diff') y-axis.
    :param group_color: (str = None) column in df to group data by.
    :param title_text: (str = 'Bland-Altman plot') title of the Bland-Altman plot.
    :param heatmap: (bool = False) if true, heatmap is showed, otherwise the scatterplot.
    :param heatmap_nbins (int = None) number of bins in the heatmap.
    :param marginal (str = None) marginal subplots of horizontal and vertical axis if heatmap is False.
    :param xlabel (str = 'Mean') x label.
    :param ylabel (str = 'Difference') y label.
    :return: (plotly.graph_objs._figure.Figure) Bland-Altman plot figure.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(df_bias_loa, pd.DataFrame):
        raise TypeError(f"df_bias_loa is of type {type(df_bias_loa).__name__}, should be pandas DataFrame")
    if not isinstance(x, str):
        raise TypeError(f"x is of type {type(x).__name__}, should be str")
    if not isinstance(y, str):
        raise TypeError(f"y is of type {type(y).__name__}, should be str")
    if not isinstance(title_text, str):
        raise TypeError(f"title_text is of type {type(title_text).__name__}, should be str")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel is of type {type(xlabel).__name__}, should be str")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel is of type {type(ylabel).__name__}, should be str")
    if not isinstance(group_color, (str, type(None))):
        raise TypeError(f"group_color is of type {type(group_color).__name__}, should be str or NoneType")
    if not isinstance(heatmap, bool):
        raise TypeError(f"heatmap is of type {type(heatmap).__name__}, should be bool")
    if not isinstance(heatmap_nbins, (int, type(None))):
        raise TypeError(f"heatmap_nbins is of type {type(heatmap_nbins).__name__}, should be int or NoneType")
    if not isinstance(marginal, (str, type(None))):
        raise TypeError(f"marginal is of type {type(marginal).__name__}, should be str or NoneType")
    if x not in df.columns:
        raise KeyError("x not existing in df")
    if y not in df.columns:
        raise KeyError("y not existing in df")
    if group_color is not None and group_color not in df.columns:
        raise KeyError("group_color not existing in df")
    if heatmap_nbins is not None and heatmap_nbins < 0:
        raise ValueError("heatmap_nbins is not an positive number")
    if marginal not in [None, 'rug', 'box', 'violin', 'histogram']:
        raise ValueError("marginal is of not None, 'rug', 'box', 'violin' or 'histogram'")

    try:
        # group_color should be column of df
        if group_color is not None:
            # sort by group_color
            df.sort_values(by=[group_color], ascending=True, inplace=True)
            df[group_color] = df[group_color].astype(str)

        x_range = np.array([np.amin(df[x]), np.amax(df[x])])  # calculate the range of min/max x-values as np.array

        def add_line(
                line: str,
                color_line: str,
                line_dash: str
        ):
            """
            Calculate the y_range, text annotations and location of annotation based on df_bias_loa. If line=='Zero',
            the zero line is added.
            """
            # calculate the y points, location of annotation and text of annotation
            if line == 'Zero':
                y_range = [0, 0]
                text_an = ''
            elif 'Slope' in df_bias_loa.index and df_bias_loa[line]['Slope'] != 0:
                y_range = df_bias_loa[line]['Intercept'] + df_bias_loa[line]['Slope'] * x_range
                text_an = "         %.2f" % df_bias_loa[line]['Intercept'] + ' + '"%.2f" % df_bias_loa[line]['Slope'] \
                          + " * " + str(x)
            elif 'Slope' not in df_bias_loa.index or df_bias_loa[line]['Slope'] == 0:
                y_range = df_bias_loa[line]['Intercept'] + 0 * x_range
                text_an = "         %.2f" % df_bias_loa[line]['Intercept']
            else:
                y_range = None
                text_an = None

            # add line
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=y_range,
                    mode="lines",  # show only lines, no markers
                    line=go.scatter.Line(
                        color=color_line,
                        dash=line_dash),
                    showlegend=False,
                )
            )

            # add annotation with additional spacing x_axis
            loc_an = [
                x_range[-1] + space_loc_an*(x_range[1] - x_range[0]),
                y_range[-1]
            ]

            fig.add_annotation(
                x=loc_an[0],
                y=loc_an[1],
                text=text_an,
                valign="top",
                align="right",
                height=height_text,  # height text above line
                font_size=size_line_text,
                showarrow=False,
                font=dict(
                    color=color_line
                )
            )

            return fig, y_range

        # heatmap or scatter
        if heatmap:
            fig = px.density_heatmap(df, x=x, y=y,
                                     nbinsx=heatmap_nbins, nbinsy=heatmap_nbins,
                                     color_continuous_scale=color_density_heatmap,
                                     )
        else:
            fig = px.scatter(
                data_frame=df,
                x=x,
                y=y,
                # hover_name='Sub',
                hover_data=df.columns,
                color=group_color,
                color_discrete_sequence=color_marker,
                marginal_x=marginal,
                marginal_y=marginal,
            )
            # change size
            fig.update_traces(marker={'size': size_marker})

        # bias and loa
        add_line(
            line='Bias',
            color_line=color_line_bias,
            line_dash=line_dash_bias
        )
        add_line(
            line='UpperLoA',
            color_line=color_line_loa,
            line_dash=line_dash_loa
        )
        add_line(
            line='LowerLoA',
            color_line=color_line_loa,
            line_dash=line_dash_loa
        )
        # zero line
        add_line(
            line='Zero',
            color_line=color_line_zero,
            line_dash=line_dash_zero
        )

        # range of x-axis and y-axis
        x_axis_range = [int(np.floor(np.amin(df[x]))), int(np.ceil(np.amax(df[x])))]
        y_axis_range = [int(np.floor(np.amin(df[y]))), int(np.ceil(np.amax(df[y])))]

        # find the extremes of the limits of agreement
        if 'Slope' in df_bias_loa.index:
            y_extreme_low_loa = np.amin(df_bias_loa['LowerLoA']['Intercept'] +
                                        df_bias_loa['LowerLoA']['Slope'] * x_range)
            y_extreme_upp_loa = np.amax(df_bias_loa['UpperLoA']['Intercept'] +
                                        df_bias_loa['UpperLoA']['Slope'] * x_range)
        elif 'Slope' not in df_bias_loa.index:
            y_extreme_low_loa = np.amin(df_bias_loa['LowerLoA']['Intercept'] + 0 * x_range)
            y_extreme_upp_loa = np.amax(df_bias_loa['UpperLoA']['Intercept'] + 0 * x_range)
        else:
            y_extreme_low_loa = None
            y_extreme_upp_loa = None
        # adapt y_axis_range if larger than yRangeUpperLoA or smaller than yRangeLowerLoA
        # lower loa
        if y_extreme_low_loa < y_axis_range[0]:
            y_axis_range[0] = y_extreme_low_loa
        # upper loa
        if y_extreme_upp_loa > y_axis_range[1]:
            y_axis_range[1] = y_extreme_upp_loa

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
            # legend=dict(font=dict(size=20)),
        )

        # change size
        fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)

        return fig

    except Exception as e:
        return e
