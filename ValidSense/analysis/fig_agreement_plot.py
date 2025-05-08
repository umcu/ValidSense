import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# variables
color_marker = px.colors.qualitative.Plotly[0]
color_line_bias = px.colors.qualitative.Plotly[0]
color_line_loa = px.colors.qualitative.Plotly[1]
line_dash_bias = 'solid'  # dash of trace lines [‘solid’, ‘dot’, ‘dash’, ‘longdash’, ‘dashdot’, ‘longdashdot’]
line_dash_loa = 'dot'  # dash of trace lines [‘solid’, ‘dot’, ‘dash’, ‘longdash’, ‘dashdot’, ‘longdashdot’]
mode = 'markers+lines'  # ['markers+lines', 'markers', 'lines']
size_plot = [1200, 700]  # [width, height]
unitX = 'hour, day'  # unit xLabel
unitY = 'mmHg'  # unit yLabel
# filter_TimeStart = datetime(year=1970, month=1, day=1, hour=0, minute=0)  # filter time start
# filter_TimeEnd = datetime(year=1970, month=1, day=9, hour=0, minute=0)  # fitler time end
filter_TimeStart = None  # filter off
filter_TimeEnd = None
size_marker = 10  # marker size
size_title = 30
size_label = 25
size_tick = 25

def fig_agreement_plot(df_bias_loa_time: pd.DataFrame, title_text = 'Agreement plot', xlabel: str = 'Time',
                       ylabel: str = 'Difference'):
    """
    Function to make the agreement plot.
    :param df_bias_loa_time: (pandas DataFrame) dataframe with bias and limits of agreement statistics.
    :param title_text: (str = 'Agreement plot') title of the agreement plot.
    :param xlabel (str = 'Time') x label.
    :param ylabel (str = 'Difference') y label.
    :return: (plotly.graph_objs._figure.Figure) agreement plot figure.
    """

    # warning
    if not isinstance(df_bias_loa_time, pd.DataFrame):
        raise TypeError(f"df_bias_loa_time is of type {type(df_bias_loa_time).__name__}, should be pandas DataFrame")
    if not isinstance(title_text, str):
        raise TypeError(f"title_text is of type {type(title_text).__name__}, should be str")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel is of type {type(xlabel).__name__}, should be str")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel is of type {type(ylabel).__name__}, should be str")

    try:
        # filter df_bias_loa_time for saving figures in thesis
        if filter_TimeStart and filter_TimeEnd is not None:
            df_bias_loa_time = df_bias_loa_time[df_bias_loa_time['TimeStart'] >= filter_TimeStart]  # filter time start
            df_bias_loa_time = df_bias_loa_time[df_bias_loa_time['TimeEnd'] <= filter_TimeEnd]  # filter time end

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_bias_loa_time['TimeStart'],
                y=df_bias_loa_time['UpperLoA'],
                name="UpperLoA",
                mode=mode,
                line=go.scatter.Line(
                    color=color_line_loa,
                    dash=line_dash_loa),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_bias_loa_time['TimeStart'],
                y=df_bias_loa_time['Bias'],
                name="Bias",
                mode=mode,
                line=go.scatter.Line(
                    color=color_line_bias,
                    dash=line_dash_bias),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_bias_loa_time['TimeStart'],
                y=df_bias_loa_time['LowerLoA'],
                name="LowerLoA",
                mode=mode,
                line=go.scatter.Line(
                    color=color_line_loa,
                    dash=line_dash_loa),
            )
        )
        fig.update_layout(
            width=size_plot[0],
            height=size_plot[1],
            title_text=title_text,
            title_font_size=size_title,
            hovermode='x',
            showlegend=False,
            xaxis_title=xlabel,
            yaxis_title=ylabel,
        )

        # fig.update_xaxes(
        #     dtick=6*60*60*1000, # tick 3 hours (unit is ms)
        #     tickformat="%H\n<b>%d<b> ",
        #     ticklabelmode="period")
        # # x_axis_range = [min(df_bias_loa_time['TimeStart']), max(df_bias_loa_time['TimeStart'])]
        # x_axis_range = [0, max(df_bias_loa_time['TimeStart']) + timedelta(hours=3)]
        # fig.update_xaxes(range=x_axis_range)

        # change size
        fig.update_traces(marker={'size': size_marker})
        fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_layout(title_font_size=size_title)

        return fig

    except Exception as e:
        return e
