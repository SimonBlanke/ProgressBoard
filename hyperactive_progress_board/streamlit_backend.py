# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import numbers
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.express as px
import plotly.graph_objects as go

try:
    from progress_io import ProgressIO
except:
    from .progress_io import ProgressIO


matplotlib.use("agg")
pd.options.mode.chained_assignment = "raise"


color_scale = px.colors.sequential.Jet


class StreamlitBackend:
    def __init__(self, progress_ids):
        self.progress_ids = progress_ids
        self.progress_id_dict = {}

        self._io_ = ProgressIO()

    def get_progress_data(self, progress_id):
        for progress_id in self.progress_ids:
            self.progress_id_dict[progress_id] = {}

            self.progress_id_dict[progress_id]["prog_d"] = self._io_.load_progress(
                progress_id
            )
            self.progress_id_dict[progress_id]["filt_f"] = self._io_.load_filter(
                progress_id
            )

        progress_data = self.progress_id_dict[progress_id]["prog_d"]

        if progress_data is None:
            return

        return progress_data[~progress_data.isin([np.nan, np.inf, -np.inf]).any(1)]

    def pyplot(self, progress_data):
        if progress_data is None or len(progress_data) <= 1:
            fig = px.line(pd.DataFrame([]))
            fig = go.Figure()
        else:
            """
            fig = px.line(
                progress_data, x="nth_iter", y="score_best", color="nth_process"
            )
            """
            fig = go.Figure()

            nth_iter = progress_data["nth_iter"]
            score_best = progress_data["score_best"]
            nth_process = list(progress_data["nth_process"])
            for i in np.unique(nth_process):
                nth_iter_p = nth_iter[nth_process == i]
                score_best_p = score_best[nth_process == i]

                fig.add_trace(
                    go.Scatter(
                        x=nth_iter_p,
                        y=score_best_p,
                        # mode="lines+markers",
                        # name="lines+markers",
                    )
                )
        """
        nth_iter = progress_data["nth_iter"]
        score_best = progress_data["score_best"]
        nth_process = list(progress_data["nth_process"])

        if np.all(nth_process == nth_process[0]):

            plt.plot(nth_iter, score_best)
        else:
            fig, ax = plt.subplots()
            ax.set_xlabel("nth iteration")
            ax.set_ylabel("best score")

            for i in np.unique(nth_process):
                nth_iter_p = nth_iter[nth_process == i]
                score_best_p = score_best[nth_process == i]
                plt.plot(nth_iter_p, score_best_p, label=str(i) + ". process")
            plt.legend()
        """
        return fig

    def get_cat_cols(self, progress_data, score=True):
        numerics = ["object", "bool", "category"]
        cat_cols = list(progress_data.select_dtypes(include=numerics).columns)
        print("\n cat_cols \n", cat_cols, "\n")

        cat_score_cols = cat_cols + ["score"]
        print("\n cat_score_cols \n", cat_score_cols, "\n")

        return progress_data[cat_score_cols]

    def get_num_cols(self, progress_data):
        numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
        return progress_data.select_dtypes(include=numerics)

    def parallel_categ(self, progress_data):
        if progress_data is None or len(progress_data) <= 1:
            fig = go.Figure()
        else:
            progress_data = self.get_cat_cols(progress_data)

            progress_data = progress_data.drop(
                ["nth_iter", "score_best", "nth_process", "best"],
                axis=1,
                errors="ignore",
            )

            # remove score
            prog_data_columns = list(progress_data.columns)
            prog_data_columns.remove("score")

            data_dict_list = []
            for col in prog_data_columns:
                data_dict = {}
                data_dict["label"] = col
                data_dict["values"] = progress_data[col]

                data_dict_list.append(data_dict)

            fig = go.Figure(
                data=go.Parcoords(
                    line=dict(
                        color=progress_data["score"],
                        colorscale=color_scale,
                    ),
                    dimensions=data_dict_list,
                )
            )

            fig = px.parallel_categories(
                progress_data,
                color_continuous_scale=color_scale,
                color="score",
                dimensions=prog_data_columns,
            )

        return fig

    def parallel_coord_(self, progress_data):
        if progress_data is None or len(progress_data) <= 1:
            fig = go.Figure()
        else:
            progress_data = self.get_num_cols(progress_data)

            progress_data = progress_data.drop(
                ["nth_iter", "score_best", "nth_process", "best"],
                axis=1,
                errors="ignore",
            )

            # remove score
            prog_data_columns = list(progress_data.columns)
            prog_data_columns.remove("score")

            data_dict_list = []
            for col in prog_data_columns:
                data_dict = {}
                data_dict["label"] = col
                data_dict["values"] = progress_data[col]

                data_dict_list.append(data_dict)

            fig = go.Figure(
                data=go.Parcoords(
                    line=dict(
                        color=progress_data["score"],
                        colorscale=color_scale,
                    ),
                    dimensions=data_dict_list,
                )
            )

        return fig

    def parallel_coord(self, progress_data):
        if progress_data is None or len(progress_data) <= 1:
            fig = px.parallel_coordinates(pd.DataFrame([]))
        else:
            progress_data = progress_data.drop(
                ["nth_iter", "score_best", "nth_process", "best"], axis=1
            )

            # remove score
            prog_data_columns = list(progress_data.columns)
            prog_data_columns.remove("score")

            fig = px.parallel_coordinates(
                progress_data,
                dimensions=prog_data_columns,
                color="score",
                color_continuous_scale=color_scale,
            )

        return fig

    def table_plotly(self, search_data):
        df_len = len(search_data)

        headerColor = "#b5beff"
        rowEvenColor = "#e8e8e8"
        rowOddColor = "white"

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(search_data.columns),
                        fill_color=headerColor,
                        align="center",
                        font_size=18,
                        height=30,
                    ),
                    cells=dict(
                        values=[search_data[col] for col in search_data.columns],
                        # fill_color="lavender",
                        fill_color=[
                            [
                                rowOddColor,
                                rowEvenColor,
                            ]
                            * int((df_len / 2) + 1)
                        ],
                        align=["center"],
                        font_size=14,
                        height=30,
                    ),
                )
            ]
        )
        fig.update_layout(height=550)
        return fig

    def create_plots(self, progress_id):
        progress_data = self.get_progress_data(progress_id)

        pyplot_fig = self.pyplot(progress_data)
        plotly_fig = self.plotly(progress_data)

        return pyplot_fig, plotly_fig

    def create_info(self, progress_id):
        progress_data = self.get_progress_data(progress_id)
        if progress_data is None or len(progress_data) <= 1:
            return None

        progress_data_best = progress_data.drop(
            ["nth_iter", "score_best", "nth_process", "best"], axis=1
        )

        progress_data_best = progress_data_best.sort_values("score")
        last_best = progress_data_best.tail(10)
        last_best = last_best.rename(
            columns={
                "score": "best 5 scores",
            }
        )

        return last_best
