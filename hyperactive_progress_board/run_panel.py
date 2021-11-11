import panel as pn

pn.extension(sizing_mode="stretch_width")
pn.extension("plotly")

from dashboard_backend import DashboardBackend


update_sec = 1

b_end = DashboardBackend()
progress_ids = b_end.progress_ids

plot_dict = {}
data_dict = {}
model_row_list = []
for progress_id in progress_ids:
    plot_dict[progress_id] = {}
    data_dict[progress_id] = {}

    search_id = progress_id.rsplit(":")[0]

    progress_data = b_end.get_progress_data(progress_id)

    pyplot_fig = b_end.line_plot_score(progress_data)
    parallel_coord_plot = b_end.parallel_coord(progress_data)
    parallel_categ_plot = b_end.parallel_categ(progress_data)
    score_hist = b_end.score_hist(progress_data)
    hist_2d = b_end.hist_2d(progress_data)

    last_best = b_end.create_info(progress_id)

    mpl_pane = pn.pane.Plotly(pyplot_fig)
    parallel_coord_pane = pn.pane.Plotly(parallel_coord_plot)
    parallel_categ_pane = pn.pane.Plotly(parallel_categ_plot)
    score_hist_pane = pn.pane.Plotly(score_hist)
    hist_2d_pane = pn.pane.Plotly(hist_2d, min_width=b_end.width(0.45))

    table_ = pn.widgets.DataFrame(progress_data, row_height=25)

    plot_dict[progress_id]["line_plot"] = mpl_pane
    plot_dict[progress_id]["parallel_coord_plot"] = parallel_coord_pane
    plot_dict[progress_id]["parallel_categ_plot"] = parallel_categ_pane
    plot_dict[progress_id]["score_hist"] = score_hist_pane
    plot_dict[progress_id]["hist_2d"] = hist_2d_pane

    plot_dict[progress_id]["table"] = table_

    # data_dict[progress_id]["parallel_coord_data"] = # pre filter incompatible paras
    # data_dict[progress_id]["parallel_categ_data"] = # pre filter incompatible paras

    title_str = """ # Objective Function: {0} """
    title_str = title_str.format(search_id)
    line_html = pn.pane.HTML(
        """<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """,
        height=1,
    )

    title_line_col = pn.Column(
        pn.pane.Markdown(title_str), line_html, pn.Spacer(height=12)
    )
    title_row = pn.Row(title_line_col)

    tabs = pn.Tabs(
        ("Parallel Coordinates", parallel_coord_pane),
        ("Parallel Categories", parallel_categ_pane),
        min_width=b_end.width(0.8),
    )

    score_plots_col = pn.Column(mpl_pane, score_hist_pane, max_width=b_end.width(0.3))

    plot1_row = pn.Row(tabs)
    plot2_row = pn.Row(
        pn.Column(pn.Spacer(height=100), table_, max_width=b_end.width(0.2)),
        score_plots_col,
        hist_2d_pane,
    )

    table_row = pn.Row(table_)

    model_row = pn.Row(
        pn.Column(title_row, plot1_row, plot2_row, table_row, background="white")
    )
    model_row_list.append(model_row)
    model_row_list.append(pn.Row(pn.Spacer(height=100), background="WhiteSmoke"))


def patch_line_plot():
    for progress_id in progress_ids:
        progress_data = b_end.get_progress_data(progress_id)
        pyplot_fig = b_end.line_plot_score(progress_data)
        plot_dict[progress_id]["line_plot"].object = pyplot_fig


def patch_parall_coord():
    for progress_id in progress_ids:
        progress_data = b_end.get_progress_data(progress_id)
        plotly_fig = b_end.parallel_coord(progress_data)
        plot_dict[progress_id]["parallel_coord_plot"].object = plotly_fig


def patch_parall_categ():
    for progress_id in progress_ids:
        progress_data = b_end.get_progress_data(progress_id)
        plotly_fig = b_end.parallel_categ(progress_data)
        plot_dict[progress_id]["parallel_categ_plot"].object = plotly_fig


def patch_hist_score():
    for progress_id in progress_ids:
        progress_data = b_end.get_progress_data(progress_id)
        score_hist_plot = b_end.score_hist(progress_data)
        plot_dict[progress_id]["score_hist"].object = score_hist_plot


def patch_hist_2d():
    for progress_id in progress_ids:
        progress_data = b_end.get_progress_data(progress_id)
        hist_2d = b_end.hist_2d(progress_data)
        plot_dict[progress_id]["hist_2d"].object = hist_2d


update_msec = 1000 * update_sec

pn.state.add_periodic_callback(patch_line_plot, update_msec)
pn.state.add_periodic_callback(patch_parall_coord, update_msec)
pn.state.add_periodic_callback(patch_parall_categ, update_msec)
pn.state.add_periodic_callback(patch_hist_score, update_msec)
pn.state.add_periodic_callback(patch_hist_2d, update_msec)


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
