import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

# variables
size_plot = [700, 500]      # width, height
size_marker = 10  # marker size
size_title = 30
size_label = 25
size_tick = 25
color_marker = px.colors.qualitative.Plotly

def fig_histogram(df, column: str='Diff', number_bins: int = 0):

    """
    Function to visualize the distribution of column in a histogram figure.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param column: (str = 'Diff') extract the distribution of this column.
    :param number_bins: (int = 0) number of bins of histogram, if 0, plotly.express.histogram automatically define the
    number of bins.
    :return: (plotly.graph_objs._figure.Figure) histogram figure.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(column, str):
        raise TypeError(f"column is of type {type(column).__name__}, should be str")
    if not isinstance(number_bins, int):
        raise TypeError(f"number_bins is of type {type(number_bins).__name__}, should be int")
    if column not in df.columns:
        raise KeyError("column not existing in df")
    if number_bins < 0:
        raise ValueError("number_bins is negative, should be positive int")
    if number_bins > len(df):
        raise ValueError("number_bins exceeds length of df")

    try:
        # set number of bins to automatic (None) when 0 is inserted for px.histogram
        if number_bins == 0:
            number_bins = None

        histogram = px.histogram(data_frame=df,
                                 x=column,
                                 nbins=number_bins,
                                 title=str('Histogram of ' + str(column)),
                                 # title=str('Histogram of difference between paired SBP measurements'),
                                 width=size_plot[0],
                                 height=size_plot[1],
                                 color_discrete_sequence=color_marker,
                                 )
        # change size
        histogram.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        histogram.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)
        histogram.update_layout(title_font_size=size_title)

        return histogram

    except Exception as e:
        return e
