# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import json
import shutil
import pandas as pd


class Messages:
    def __init__(self, verbosity, warnings):
        self.verbosity = verbosity
        self.warnings = warnings

    def load_progress_file(self, path):
        if self.verbosity:
            print("Load progress data file from path:", path)

    def progress_file_not_found(self, path):
        if self.warnings:
            print("Warning: Progress data not found in:", path)

    def remove_progress_data(self, path):
        if self.verbosity:
            print("Remove progress data file from path:", path)

    def remove_lock_file(self, path):
        if self.verbosity:
            print("Remove lock file from path:", path)


class Paths:
    here = os.path.dirname(os.path.abspath(__file__))
    path = here + "/tmp_files/"

    def get_progress_data_path(self, search_id):
        return self.path + "/progress_data_" + search_id + ".csv"

    def get_lock_file_path(self, search_id):
        return self.path + "/progress_data_" + search_id + ".csv.lock"

    def get_config_path(self):
        return self.path + "/config.json"


class ProgressIO(Paths):
    def __init__(self, verbosity=True, warnings=True):
        self.msg = Messages(verbosity, warnings)

    def create_init(self):
        init_file = os.path.join(self.path, "__init__.py")
        if not os.path.exists(init_file):
            os.mknod(init_file)

    def create_pd_path(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path)

    def read_config(self):
        with open(self.get_config_path(), "r", encoding="utf-8") as f:
            config_d = json.load(f)
        return config_d

    def save_config(self, config_d):
        with open(self.get_config_path(), "w", encoding="utf-8") as f:
            json.dump(config_d, f, ensure_ascii=False, indent=4)

    def load_progress(self, search_id):
        path = self.get_progress_data_path(search_id)
        if os.path.isfile(path):
            self.msg.load_progress_file(path)
            return pd.read_csv(path)
        else:
            self.msg.progress_file_not_found(path)
            return None

    def remove_progress(self, search_id):
        path = self.get_progress_data_path(search_id)
        if os.path.isfile(path):
            os.remove(path)
            self.msg.remove_progress_data(path)

    def remove_lock(self, search_id):
        path = self.get_lock_file_path(search_id)
        if os.path.isfile(path):
            os.remove(path)
            self.msg.remove_lock_file(path)
