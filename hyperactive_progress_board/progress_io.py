# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
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


class ProgressIO:
    def __init__(self, verbosity=True, warnings=True):
        here = os.path.dirname(os.path.abspath(__file__))
        self.path = here + "/progress_data/"

        self.msg = Messages(verbosity, warnings)

    def create_pd_path(self):
        if os.path.exists(self.path):

            shutil.rmtree(self.path)

        os.makedirs(self.path)

    def get_progress_data_path(self, search_id):
        return self.path + "/progress_data_" + search_id + ".csv"

    def get_lock_file_path(self, search_id):
        return self.path + "/progress_data_" + search_id + ".csv.lock"

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
