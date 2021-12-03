# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import os
import time
import json
import uuid
from shutil import copyfile

import numpy as np

from hyperactive_data_storage import DataSaver
from .progress_io import ProgressIO


class ProgressBoard:
    def __init__(self, width=2400):
        self.width = width

        self.uuid = uuid.uuid4().hex
        self.progress_ids = []

        self._io_ = ProgressIO(verbosity=False)
        self._io_.create_pd_path()

        self.progress_collectors = {}

        self.best = 0
        self.nth_iter = 0
        self.best_para = None
        self.best_score = -np.inf

    def get_best(self, score, para):
        self.nth_iter += 1

        if score > self.best_score:
            self.best_score = score
            self.best_para = para
            self.best = 1
        else:
            self.best = 0

    def update(self, objective_function):
        self.init_paths(objective_function.__name__)

        def wrapper(para):
            c_time = time.time()
            results = objective_function(para)
            d_time = time.time() - c_time

            progress_id = objective_function.__name__ + ":" + self.uuid

            if isinstance(results, tuple):
                score = results[0]
                results_dict = results[1]
            else:
                score = results
                results_dict = {}

            # keep track on best score and para
            self.get_best(score, para)

            results_dict["score"] = score
            progress_dict = para.para_dict

            progress_dict.update(results_dict)
            progress_dict["score_best"] = self.best_score
            progress_dict["nth_iter"] = self.nth_iter
            progress_dict["best"] = self.best
            progress_dict["eval time"] = d_time

            progress_dict["nth_process"] = para.nth_process

            self.progress_collectors[progress_id].append(progress_dict)

            return results

        wrapper.__name__ = objective_function.__name__

        return wrapper

    def create_lock(self, progress_id):
        path = self._io_.get_lock_file_path(progress_id)
        if not os.path.exists(path):
            os.mknod(path)

    def init_paths(self, search_id):
        progress_id = search_id + ":" + self.uuid
        self.progress_ids.append(progress_id)

        self.create_lock(progress_id)
        data_c = DataSaver(self._io_.get_progress_data_path(progress_id))
        self.progress_collectors[progress_id] = data_c

    def create_tmp_panels(self):
        abspath = os.path.abspath(__file__)

        panel_paths = []
        dashboard_path = os.path.join(os.path.dirname(abspath), "run_panel.py")
        for progress_id in self.progress_ids:
            panel_path = os.path.join(
                os.path.dirname(abspath),
                "tmp_files",
                progress_id + ".py",
            )
            copyfile(dashboard_path, panel_path)

            panel_paths.append(panel_path)
        return " ".join(panel_paths)

    def open(self):
        config_d = {"width": self.width, "progress_ids": self.progress_ids}

        self._io_.create_init()
        self._io_.save_config(config_d)

        panel_paths_tmp = self.create_tmp_panels()

        open_streamlit = "panel serve --show " + panel_paths_tmp

        # from: https://stackoverflow.com/questions/7574841/open-a-terminal-from-python
        os.system('gnome-terminal -x bash -c " ' + open_streamlit + ' " ')
