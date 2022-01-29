from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.datasets import fetch_california_housing

from hyperactive import Hyperactive
from hyperactive_progress_board import ProgressBoard


def test_progress_board():
    data = fetch_california_housing()
    X, y = data.data, data.target

    progress = ProgressBoard()

    @progress.update
    def dtr_model(opt):
        dtr = DecisionTreeRegressor(
            min_samples_split=opt["min_samples_split"],
        )
        scores = cross_val_score(dtr, X, y, cv=3)
        return scores.mean()

    search_space = {
        "max_depth": list(range(2, 50)),
        "min_samples_split": list(range(2, 50)),
        "min_samples_leaf": list(range(1, 50)),
    }

    progress.open()

    hyper = Hyperactive()
    hyper.add_search(dtr_model, search_space, n_iter=20)
    hyper.run()
