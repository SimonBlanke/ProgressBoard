import os
import sys
import time
import numpy as np
import pandas as pd
import panel as pn

pn.extension(sizing_mode="stretch_width")
pn.extension("plotly")

from streamlit_backend import StreamlitBackend


progress_ids = sys.argv[1:]
backend = StreamlitBackend(progress_ids)


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

    plot_dict[progress_id]["line_plot"] = mpl_pane

    plot_dict[progress_id]["parallel_coord_plot"] = parallel_coord_pane
    plot_dict[progress_id]["parallel_categ_plot"] = parallel_categ_pane

    # data_dict[progress_id]["parallel_coord_data"] = # pre filter incompatible paras
    # data_dict[progress_id]["parallel_categ_data"] = # pre filter incompatible paras

    """
    if last_best is not None:
        plotly_table = backend.table_plotly(last_best)
        placeholder3.plotly_chart(plotly_table, use_container_width=True)
    """

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
    table_row = pn.Row()

    model_row = pn.Row(pn.Column(title_row, plot_row, background="white"))
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
        plotly_fig = backend.parallel_coord(progress_data)
        plot_dict[progress_id]["parallel_coord_plot"].object = plotly_fig


def patch_parall_categ():
    for progress_id in progress_ids:
        progress_data = backend.get_progress_data(progress_id)
        print("\n progress_data \n ", progress_data.dtypes, "\n")
        plotly_fig = backend.parallel_categ(progress_data)
        plot_dict[progress_id]["parallel_categ_plot"].object = plotly_fig


pn.state.add_periodic_callback(patch_line_plot, 1000)
pn.state.add_periodic_callback(patch_parall_coord, 1000)
pn.state.add_periodic_callback(patch_parall_categ, 1000)


main_col = pn.Column(*model_row_list)
layout = pn.layout.GridBox(main_col, sizing_mode="stretch_both")

pn.template.FastListTemplate(
    site="Hyperactive",
    title="Progress Board",
    main=[
        layout,
    ],
).servable()
