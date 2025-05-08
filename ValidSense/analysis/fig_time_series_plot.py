import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# variables
# mode = 'markers+lines'  # ['markers+lines', 'markers', 'lines']
size_plot = [1200, 700]  # [width, height]
unitX = 'hour, day'  # unit xLabel
unitY = 'mmHg'  # unit yLabel
x_axis = 'Time at EntryBP (' + unitX + ')'  # label x-axis
y1_axis = 'Dev1, Dev2 (' + unitY + ')'  # label y-axis
y2_axis = 'Diff (' + unitY + ')'  # label y-axis
# filter_TimeStart = datetime(year=1970, month=1, day=1, hour=0, minute=0)  # filter time start
# filter_TimeEnd = datetime(year=1970, month=1, day=9, hour=0, minute=0)  # fitler time end
filter_TimeStart = None  # filter off
filter_TimeEnd = None
line_dash = ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
marker_dash = ['circle', 'square', 'diamond' ,'cross', 'x', 'asterisk', 'x-thin']
color_marker = px.colors.qualitative.Plotly
line_width = 5
size_marker = 5  # marker size
size_title = 30
size_label = 25
size_tick = 25

def fig_time_series_plot(df: pd.DataFrame, x: str, y1: str = 'Dev1', y2: str = 'Dev2',
                    title_text: str = 'Time series',
                    xlabel: str = 'Time',
                    ylabel: str = 'Dev1 & Dev2',
                    group_color: str = None,
                    show_dev1: bool = True,
                    show_dev2: bool = True,
                    show_dev1_trend: bool = True,
                    show_dev2_trend: bool = True,
                    entry_bp: str = None,
                    window_size_trendline: int = 5,
                    ):
    """
    Function to make a time series plot scatterplot with trendlines.
    :param df: (pandas DataFrame) dataframe with all measurements
    :param x: (str) x-axis indicating time.
    :param y1: (str = 'Dev1') y-axis Dev1.
    :param y2: (str = 'Dev2') y-axis Dev2.
    :param group_color: (str = None) column in df to group data by.
    :param title_text: (str) = Time series individual subjects') title of figure.
    :param xlabel (str = 'Time') x label.
    :param ylabel (str = 'Dev1 & Dev2') y label.
    :param show_dev1: (bool = True) show timeseries Dev1.
    :param show_dev2: (bool = True) show timeseries Dev2.
    :param show_dev1_trend: (bool = True) show scatter of dev1.
    :param show_dev2_trend: (bool = True) show scatter of dev2.
    :param entry_bp: (str = None) column indicating EntryBP.
    :param window_size_trendline: (int = 30) window size of trendline moving (median) average
    :return: (plotly.graph_objs._figure.Figure) ) time series  figure of individual subjects with moving (median) average.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(group_color, str ):
        raise TypeError(f"group_color is of type {type(group_color).__name__}, should be str")
    if group_color not in df.columns:
        raise KeyError("group_color not existing in df")
    if entry_bp is not None and entry_bp not in df.columns:
        raise KeyError("entry_bp not existing in df")
    if not isinstance(x, str):
        raise TypeError(f"x is of type {type(x).__name__}, should be str")
    if not isinstance(y1, str):
        raise TypeError(f"y1 is of type {type(y1).__name__}, should be str")
    if not isinstance(y2, str):
        raise TypeError(f"y2 is of type {type(y2).__name__}, should be str")
    if not isinstance(entry_bp, (str, type(None))):
        raise TypeError(f"entry_bp is of type {type(entry_bp).__name__}, should be str or NoneType")
    if not isinstance(show_dev1, bool):
        raise TypeError(f"show_dev1 is of type {type(show_dev1).__name__}, should be bool")
    if not isinstance(show_dev2, bool):
        raise TypeError(f"show_dev2 is of type {type(show_dev2).__name__}, should be bool")
    if not isinstance(show_dev1_trend, bool):
        raise TypeError(f"show_dev1_trend is of type {type(show_dev1_trend).__name__}, should be bool")
    if not isinstance(show_dev2_trend, bool):
        raise TypeError(f"show_dev2_trend is of type {type(show_dev2_trend).__name__}, should be bool")
    if x not in df.columns:
        raise KeyError("x not existing in df")
    if y1 not in df.columns:
        raise KeyError("y1 not existing in df")
    if y1 not in df.columns:
        raise KeyError("y2 not existing in df")
    if not isinstance(title_text, str):
        raise TypeError(f"title_text is of type {type(title_text).__name__}, should be str")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel is of type {type(xlabel).__name__}, should be str")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel is of type {type(ylabel).__name__}, should be str")


    try:
        # filter df_bias_loa_time for saving figures in thesis
        if filter_TimeStart and filter_TimeEnd is not None:
            df = df[df[x] >= filter_TimeStart]  # filter time start
            df = df[df[x] <= filter_TimeEnd]  # filter time end

        if entry_bp != None:
            # time relative to entry point
            groups = df.groupby(group_color)  # group
            time_relative = []  # empty list
            for name, group in groups:  # loop through each group
                timestamp_entry = group.loc[group['EntryBP'] == 1, x].iloc[0]  # find entryBP is 1
                time_relative.extend(
                    (group[x] - timestamp_entry).tolist())  # subtract timestamp_entry from timestamp
            ColTimeRelativeEntryBP = 'TimeRelativeEntryBP'
            df[ColTimeRelativeEntryBP] = pd.DataFrame(time_relative) + pd.to_datetime('1970/01/01') # add to df
            df = df.sort_values([group_color, ColTimeRelativeEntryBP], ascending=[True, True])  # sort
            xaxis=ColTimeRelativeEntryBP
        else:
            xaxis='Datetime'
            df = df.sort_values([xaxis], ascending=True)  # sort

        # median moving average
        df_smoothed1 = df.groupby(group_color).apply(lambda x: x[y1].rolling(window_size_trendline, center=True).median())
        df_smoothed2 = df.groupby(group_color).apply(lambda x: x[y2].rolling(window_size_trendline, center=True).median())

        # figure
        fig = make_subplots(specs=[[{"secondary_y": True}]])  # subplots with two y-axis
        grouped_df = df.groupby(group_color)  # group

        count = 0  # count for colors
        for name, group in grouped_df:
            if show_dev1:
                # dots dev1
                fig.add_trace(
                    go.Scatter(x=group[xaxis], y=group[y1], mode='markers',
                               marker=dict(color=color_marker[count], symbol=marker_dash[0], size=size_marker,
                                           line=dict(width=0.5, color="DarkSlateGrey")),
                               name=f'{name} {y1}'),
                    secondary_y=False,
                )
                # dots dev2
            if show_dev2:
                fig.add_trace(
                    go.Scatter(x=group[xaxis], y=group[y2], mode='markers',
                               marker=dict(color=color_marker[count], symbol=marker_dash[4], size=size_marker,
                                           line=dict(width=0.5, color="DarkSlateGrey")),
                               name=f'{name} {y2}'),
                    secondary_y=False,
                )
            if show_dev1_trend:
                # trendline dev1
                fig.add_trace(
                    go.Scatter(x=group[xaxis], y=df_smoothed1[name].values, mode='lines',
                               line=dict(color=color_marker[count], dash=line_dash[1], width=line_width),
                               name=f'{name} Trend {y1}'),
                    secondary_y=False,
                )
            if show_dev2_trend:
                # trendline dev2
                fig.add_trace(
                    go.Scatter(x=group[xaxis], y=df_smoothed2[name].values, mode='lines',
                               line=dict(color=color_marker[count], dash=line_dash[0], width=line_width),
                               name=f'{name} Trend {y2}'),
                    secondary_y=False,
                )
            count += 1  # count to walk through back to 0 if it exceeds 20
            if count == 10:
                count = 0

        fig.update_layout(  # axis
            xaxis_title=x_axis,
            yaxis=dict(title=y1_axis, showgrid=False, zeroline=False),
            yaxis2=dict(title=y2_axis, overlaying='y', side='right', showgrid=False, zeroline=False),
        )

        fig.update_traces(
            marker=dict(size=size_marker)
        )
        fig.update_layout(
            width=size_plot[0],
            height=size_plot[1],
            title_text=title_text,
            xaxis_title=xlabel,
            yaxis_title=ylabel,
        )

        # other ticks
        # fig.update_xaxes(
        #     dtick=60*60*1000, # tick 3 hours (unit is ms)
        #     tickformat="%H\n<b>%d<b> ",
        #     ticklabelmode="period")
        # x_axis_range = [0, max(df[xaxis]) + timedelta(hours=3)]
        # fig.update_xaxes(range=x_axis_range)

        # change size
        fig.update_traces(marker={'size': size_marker})
        fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_layout(title_font_size=size_title)

        return fig

    except Exception as e:
        print(e)
        return e
