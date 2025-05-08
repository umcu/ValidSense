from scipy import stats as stats
from statsmodels.graphics.gofplots import qqplot
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

# source:
# https://plotly.com/python/v3/normality-test/
# https://www.statsmodels.org/dev/generated/statsmodels.graphics.gofplots.qqplot.html

# variables
size_plot = [700, 700]  # width, height
dist = stats.norm   # normal distribution
size_marker = 5  # marker size
size_title = 30
size_label = 25
size_tick = 25


def fig_qq_plot(df, column: str = 'Diff', line: str = 's', fit: bool = True):
    """
    Function to create a probability distributions by plotting their quantiles against each other.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param column: (str = 'Diff') extract the distribution of this column.
    :param line: (str or None = 's') options for the reference line to which the data is compared: “45” - 45-degree
    line, “s” - standardized line, the expected order statistics are scaled by the standard deviation of the given
    sample and have the mean added to them, “r” - A regression line is fit, “q” - A line is fit through the quartiles,
    None - by default no reference line is added to the plot.
    :param fit: (bool = True) the quantiles are formed from the standardized data.
    :return: (plotly.graph_objs._figure.Figure) Q-Q plot figure.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(column, str):
        raise TypeError(f"column is of type {type(column).__name__}, should be str")
    if not isinstance(line, (str, type(None))):
        raise TypeError(f"line is of type {type(line).__name__}, should be str or NoneType")
    if not isinstance(fit, bool):
        raise TypeError(f"fit is of type {type(fit).__name__}, should be bool")
    if column not in df.columns:
        raise KeyError("column not existing in df")
    if line not in [None, '45', 's', 'r', 'q']:
        raise KeyError("line should be None, '45', 's', 'r', 'q'.")

    try:
        qq_plot_data = qqplot(data=df[column], line=line, fit=fit, dist=dist).gca().lines

        fig = go.Figure()

        # show quantiles
        fig.add_trace({
            'type': 'scatter',
            'x': qq_plot_data[0].get_xdata(),
            'y': qq_plot_data[0].get_ydata(),
            'mode': 'markers',
            'marker': {
                'color': px.colors.qualitative.Plotly[0]
            }
        })

        # show line if line is not None
        if line != None:
            fig.add_trace({
                'type': 'scatter',
                'x': qq_plot_data[1].get_xdata(),
                'y': qq_plot_data[1].get_ydata(),
                'mode': 'lines',
                'line': {
                    'color': px.colors.qualitative.Plotly[1]
                }
            })

        # change layout
        fig['layout'].update({
            'title': str('Q-Q plot of ' + str(column)),
            # 'title': str('Q-Q plot of ' + str(column) + ' in BP change levels CPC measurements (mixed effect model)'),
            'xaxis': {
                'title': 'Theoritical Quantities',
                'zeroline': False
            },
            'yaxis': {
                'title': 'Sample Quantities'
            },
            'showlegend': False,
            'width': size_plot[0],
            'height': size_plot[1],
        })

        # change size
        fig.update_traces(marker={'size': size_marker})
        fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_layout(title_font_size=size_title)

        return fig

    except Exception as e:
        return e
