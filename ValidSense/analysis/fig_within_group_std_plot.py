import pandas as pd
import numpy as np
import plotly.express as px

size_plot = [700, 700]  # [width, height]
spac = [1, 5]  # additional spacing: [x_axis_range, y_axis_range]
size_marker = 10  # marker size
size_title = 30
size_label = 25
size_tick = 25
color_marker = px.colors.qualitative.Plotly

def fig_within_group_std_plot(df: pd.DataFrame, group: str):
    """
    Function to create the within-group standard deviation plot.
    :param df: (pandas DataFrame) dataframe with column 'mean' and 'diff', representing the mean and difference.
    :param group: (str) column in df to group by.
    :return: (plotly.graph_objs._figure.Figure) Within-Group Std plot figure.
    """

    # warning
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df is of type {type(df).__name__}, should be pandas DataFrame")
    if not isinstance(group, str):
        raise TypeError(f"group is of type {type(group).__name__}, should be str")
    if 'Diff' not in df.columns:
        raise KeyError("Diff not existing in df")
    if 'Mean' not in df.columns:
        raise KeyError("Mean not existing in df")
    if group not in df.columns:
        raise KeyError("group not existing in df")
    if df['Diff'].isnull().values.any():
        raise ValueError("Diff contains missing values")
    if df['Mean'].isnull().values.any():
        raise ValueError("Mean contains missing values")
    if df[group].isnull().values.any():
        raise ValueError("group contains missing values")


    try:
        # find unique groups
        find_group = df[group].unique()  # find unique groups

        # average_group = (Dev1 + Dev2) / 2, for every row, grouped
        # diff = Dev1 - Dev2, for every row, grouped
        # average_mean = mean(average), grouped
        # diff_std = std(diff), grouped

        # empty list
        std_diff_group = []
        mean_average_group = []
        number_obs = []

        for ind in range(len(find_group)):  # loop ind for length of find_group
            # average per group (group equal to find_group[ind])
            average_group = df['Mean'][df[group] == find_group[ind]]
            # difference per group
            diff_group = df['Diff'][df[group] == find_group[ind]]
            # std of difference_group
            std_diff_group += [np.std(diff_group)]
            # mean of average_group
            mean_average_group += [np.mean(average_group)]
            # number of observations within group
            number_obs += [len(average_group)]

        # dataframe with group mean and std of diff
        # name_x = f"{group} mean"
        name_x = f"{group}-mean"
        name_y = f"Within-{group}-SD"
        res = pd.DataFrame(
            {group: find_group,
             name_x: mean_average_group,
             name_y: std_diff_group})

        # within group std plot
        fig = px.scatter(data_frame=res,
                        x=name_x,
                        y=name_y,
                        # title=str('Within-cluster-SD plot'),
                        title=str('Within-' + group + '-SD plot'),
                        # title=str('Within-subject SD plot in BP change levels CPC measurements (mixed effect model)'),
                        size=number_obs,           # area of circle is proportional to number of observations
                        width=size_plot[0],
                        height=size_plot[1],
                        hover_data=res.columns,
                        color_discrete_sequence=color_marker,
                        )

        # range of x-axis and y-axis
        x_axis_range = [int(np.floor(np.amin(res[name_x])) - spac[0]),
                        int(np.ceil(np.amax(res[name_x])) + spac[0])]       # x range: min to max
        y_axis_range = [0, int(np.ceil(np.amax(res[name_y])) + spac[1])]    # x range: 0 to max
        fig.update_xaxes(range=x_axis_range)
        fig.update_yaxes(range=y_axis_range)

        # change labels
        fig.update_xaxes(title_text=str(group + ' mean'))  # x label
        fig.update_yaxes(title_text=str('Within-' + group + ' SD'))  # y label

        # change size
        fig.update_traces(marker={'size': size_marker})
        fig.update_xaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_yaxes(tickfont_size=size_tick, title_font_size=size_label)
        fig.update_layout(title_font_size=size_title)

        return fig

    except Exception as e:
        return e

# see Bland-Altman 1999, section 3 figure 3
