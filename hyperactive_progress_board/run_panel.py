import os
import sys
import time
import numpy as np
import pandas as pd
import panel as pn

pn.extension(sizing_mode="stretch_width")
pn.extension("plotly")

from dashboard_backend import DashboardBackend


update_sec = 1


progress_ids = sys.argv[1:]
backend = DashboardBackend(progress_ids)

print("\n -----------> progress_ids \n", progress_ids, "\n")

plot_dict = {}
data_dict = {}
model_row_list = []
for progress_id in progress_ids:
    plot_dict[progress_id] = {}
    data_dict[progress_id] = {}

    search_id = progress_id.rsplit(":")[0]

    progress_data = backend.get_progress_data(progress_id)

    pyplot_fig = backend.pyplot(progress_data)
    parallel_coord_plot = backend.parallel_coord(progress_data)
    parallel_categ_plot = backend.parallel_categ(progress_data)

    last_best = backend.create_info(progress_id)

    mpl_pane = pn.pane.Plotly(pyplot_fig)
    parallel_coord_pane = pn.pane.Plotly(parallel_coord_plot)
    parallel_categ_pane = pn.pane.Plotly(parallel_categ_plot)
    tabulator = pn.widgets.Tabulator(last_best, height=500)

    plot_dict[progress_id]["line_plot"] = mpl_pane
    plot_dict[progress_id]["parallel_coord_plot"] = parallel_coord_pane
    plot_dict[progress_id]["parallel_categ_plot"] = parallel_categ_pane
    plot_dict[progress_id]["table"] = tabulator

    # data_dict[progress_id]["parallel_coord_data"] = # pre filter incompatible paras
    # data_dict[progress_id]["parallel_categ_data"] = # pre filter incompatible paras

    title_str = """ # Objective Function: {0} """
    title_str = title_str.format(search_id)
    line_html = pn.pane.HTML(
        """<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """,
        height=1,
    )

    title_line_col = pn.Column(
        pn.pane.Markdown(title_str), line_html, pn.Spacer(height=10)
    )
    title_row = pn.Row(title_line_col)

    tabs = pn.Tabs(
        ("Parallel Coordinates", parallel_coord_pane),
        ("Parallel Categories", parallel_categ_pane),
    )

    plot_row = pn.Row(mpl_pane, tabs)
    table_row = pn.Row(tabulator)

    model_row = pn.Row(pn.Column(title_row, plot_row, table_row, background="white"))
    model_row_list.append(model_row)
    model_row_list.append(pn.Row(pn.Spacer(height=100), background="WhiteSmoke"))


def patch_line_plot():
    for progress_id in progress_ids:
        progress_data = backend.get_progress_data(progress_id)
        pyplot_fig = backend.pyplot(progress_data)
        plot_dict[progress_id]["line_plot"].object = pyplot_fig


def patch_parall_coord():
    for progress_id in progress_ids:

        progress_data = backend.get_progress_data(progress_id)
        print("\n progress_data \n", progress_data, "\n")

        plotly_fig = backend.parallel_coord(progress_data)
        plot_dict[progress_id]["parallel_coord_plot"].object = plotly_fig


def patch_parall_categ():
    for progress_id in progress_ids:
        progress_data = backend.get_progress_data(progress_id)
        plotly_fig = backend.parallel_categ(progress_data)
        plot_dict[progress_id]["parallel_categ_plot"].object = plotly_fig


def stream_table():
    progress_data_new = backend.diff_progress_data
    # print("\n progress_data_new \n", progress_data_new, "\n")
    if len(progress_data_new) > 0:
        plot_dict[progress_id]["table"].stream(progress_data_new, rollover=10)
    else:
        print("\n ---> No new progress data for table stream")


update_msec = 1000 * update_sec

pn.state.add_periodic_callback(patch_line_plot, update_msec)
pn.state.add_periodic_callback(patch_parall_coord, update_msec)
pn.state.add_periodic_callback(patch_parall_categ, update_msec)
# pn.state.add_periodic_callback(stream_table, update_msec)


main_col = pn.Column(*model_row_list)
layout = pn.layout.GridBox(main_col, sizing_mode="stretch_both")

pn.template.FastListTemplate(
    site="Hyperactive",
    title="Progress Board",
    main=[
        layout,
    ],
    header_background="#544763",
).servable()
