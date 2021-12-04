import os
import panel as pn
import holoviews as hv

import numpy as np
import pandas as pd

from hyperactive_progress_board.dashboard_backend import DashboardBackend

pn.extension(sizing_mode="stretch_both")
# pn.extension("plotly")


update_sec = 1

b_end = DashboardBackend()
progress_id = os.path.basename(__file__).split(".", 1)[0]

plot_dict = {}


progress_data = b_end.get_progress_data_wait(progress_id)


pyplot_fig = b_end.line_plot_score(progress_data)
parallel_coord_plot = b_end.parallel_coord(progress_data)
parallel_categ_plot = b_end.parallel_categ(progress_data)
score_hist = b_end.score_1d_hist(progress_data)


mpl_pane = pn.pane.Plotly(pyplot_fig)
parallel_coord_pane = pn.pane.Plotly(parallel_coord_plot)
parallel_categ_pane = pn.pane.Plotly(parallel_categ_plot)
score_hist_pane = pn.pane.Plotly(score_hist)


row_height = 35
last_10, best_10, worst_10 = b_end.create_dfs(progress_id)


table_last = b_end.table_plotly(last_10)
table_best = b_end.table_plotly(best_10)
table_worst = b_end.table_plotly(worst_10)


table_last = pn.widgets.DataFrame(
    last_10, show_index=False, index_names=False, row_height=row_height
)
table_best = pn.widgets.DataFrame(
    best_10, show_index=False, index_names=False, row_height=row_height
)
table_worst = pn.widgets.DataFrame(
    worst_10, show_index=False, index_names=False, row_height=row_height
)

table_tabs = pn.Tabs(
    ("Last 10", table_last), ("Best 10", table_best), ("Worst 10", table_worst)
)


plot_dict["line_plot"] = mpl_pane
plot_dict["parallel_coord_plot"] = parallel_coord_pane
plot_dict["parallel_categ_plot"] = parallel_categ_pane
plot_dict["score_hist"] = score_hist_pane

plot_dict["table"] = table_tabs


"""
def create_filters(df, orientation="horz"):
    paras = list(df.columns)
    filter_d = {}

    if orientation == "horz":
        orient = "horizontal"
        inline = True
    elif orientation == "vert":
        orient = "vertical"
        inline = False

    for para in paras:
        para_data = df[para].values

        try:
            min_ = np.amin(para_data)
            max_ = np.amax(para_data)
            step_ = (max_ - min_) / 100
        except:
            filter_d[para] = pn.widgets.CheckBoxGroup(
                name=str(para),
                value=list(set(para_data)),
                options=list(set(para_data)),
                inline=inline,
            )
        else:
            filter_d[para] = pn.widgets.RangeSlider(
                name=str(para),
                start=min_,
                end=max_,
                step=step_,
                orientation=orient,
            )

    filter_l = list(filter_d.values())

    return pn.Column(*filter_l, height=40 * len(filter_l)), filter_d
"""

paral_coord_col = pn.Column(parallel_coord_pane)
parallel_plot_tabs = pn.Tabs(
    ("Parallel Coordinates", paral_coord_col),
    ("Parallel Categories", parallel_categ_pane),
)


def update_widgets():
    progress_data = b_end.get_progress_data(progress_id)

    pyplot_fig = b_end.line_plot_score(progress_data)
    paral_crd_plt = b_end.parallel_coord(progress_data)
    paral_cat_plt = b_end.parallel_categ(progress_data)
    score_hist_plot = b_end.score_1d_hist(progress_data)
    table_ = b_end.table_plotly(progress_data)

    plot_dict["line_plot"].object = pyplot_fig
    plot_dict["parallel_coord_plot"].object = paral_crd_plt
    plot_dict["parallel_categ_plot"].object = paral_cat_plt
    plot_dict["score_hist"].object = score_hist_plot

    last_10, best_10, worst_10 = b_end.create_dfs(progress_id)

    """
    plot_dict["table"][0].object = last_10
    plot_dict["table"][1].object = best_10
    plot_dict["table"][2].object = worst_10
    """
    plot_dict["table"][0].patch(last_10)
    plot_dict["table"][1].patch(best_10)
    plot_dict["table"][2].patch(worst_10)


update_msec = 1000 * update_sec

pn.state.add_periodic_callback(update_widgets, update_msec)


app = pn.template.FastGridTemplate(
    site="Hyperactive Progress Board",
    title=progress_id.rsplit(":")[0],
    prevent_collision=True,
    row_height=150,
    header_background="#544763",
)

app.main[0:3, 0:12] = parallel_plot_tabs
app.main[3:6, 0:6] = mpl_pane
app.main[3:6, 6:12] = score_hist_pane
app.main[6:9, 0:12] = table_tabs


app.servable()
