<H1 align="center">
    Progress Board
</H1>


<p align="center">
  <a href="https://github.com/SimonBlanke/ProgressBoard/actions">
    <img src="https://github.com/SimonBlanke/ProgressBoard/actions/workflows/tests.yml/badge.svg?branch=main" alt="img not loaded: try F5 :)">
  </a>
  <a href="https://app.codecov.io/gh/SimonBlanke/ProgressBoard">
    <img src="https://img.shields.io/codecov/c/github/SimonBlanke/ProgressBoard/main&logo=codecov" alt="img not loaded: try F5 :)">
  </a>
</p>


<H2 align="center">
    An addon for the Hyperactive package to visualize the progress of optimization runs.
</H2>



<td> <img src="./docs/output.gif" width="100%"> </td>


<br>

The Progress Board is a dashboard (opens in webbrowser) that provides visualization of live-updated data from Hyperactive. It integrates seamlessly with Hyperactive (v4) and opens up the optimization run with useful information. It also supports multiprocessing and multiple searches at the same time without any added complexity or work for the user. 

The Progress Board should be used for computationally expensive objective functions (like machine-/deep-learning models). 

The Progress Board is tested in Ubuntu, but Windows support maybe added in the future.


<br>

## State of project

### This project is in an early development stage. If you encounter a problem it would be very helpful to open an issue and describe it in detail.


<br>

## Installation

```console
pip install hyperactive-progress-board
```

<br>

## Example

```python
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.datasets import fetch_california_housing

from hyperactive import Hyperactive
from hyperactive_progress_board import ProgressBoard # import progress board

data = fetch_california_housing()
X, y = data.data, data.target

progress = ProgressBoard() # init progress board


@progress.update # add decorator
def dtr_model(opt):
    dtr = DecisionTreeRegressor(
        min_samples_split=opt["min_samples_split"],
    )
    scores = cross_val_score(dtr, X, y, cv=5)
    return scores.mean()


search_space = {
    "max_depth": list(range(2, 50)),
    "min_samples_split": list(range(2, 50)),
    "min_samples_leaf": list(range(1, 50)),
}

progress.open() # open progress board before run begins

hyper = Hyperactive()
hyper.add_search(dtr_model, search_space, n_iter=1000)
hyper.run()
```

<br>

## FAQ

<details>
<summary> Command line opens and closes immediately </summary>

<br>

This happens because of the command line of a previous run of the progress-board is still running. Close the command-line from the previous run to start a new one.

</details>





