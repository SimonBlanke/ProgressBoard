# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import json
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


class DashboardBackend:
    def __init__(self):
        self._io_ = ProgressIO()
        config_d = self._io_.read_config()

        self.width = config_d["width"]
        self.progress_ids = config_d["progress_ids"]

        self.current_progress_data = None
        self.diff_progress_data = None

    def get_progress_data(self, progress_id):
        progress_data = self._io_.load_progress(progress_id)
        if progress_data is None:
            return
        return progress_data[~progress_data.isin([np.nan, np.inf, -np.inf]).any(1)]

    def pyplot(self, progress_data):
        if progress_data is None or len(progress_data) <= 1:
            fig = px.line(pd.DataFrame([]))
            fig = go.Figure()
        else:
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
                    )
                )

        return fig

    def get_cat_cols(self, progress_data, score=True):
        numerics = ["object", "bool", "category"]
        cat_cols = list(progress_data.select_dtypes(include=numerics).columns)
        cat_score_cols = cat_cols + ["score"]

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

    def score_hist(self, progress_data):
        if progress_data is None or len(progress_data) <= 1:
            # fig = go.Figure()
            fig = px.histogram(pd.DataFrame([]))
        else:
            scores = progress_data["score"]
            # fig = go.Figure(data=[go.Histogram(x=scores)])
            fig = px.histogram(progress_data, x="score")

        return fig

    def hist_2d(self, progress_data):
        if progress_data is None or len(progress_data) <= 1:
            # fig = go.Figure()
            fig = px.histogram(pd.DataFrame([]))
        else:
            scores = progress_data["score"]
            fig = px.scatter(
                progress_data, x="min_samples_split", y="x1", color="score"
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
