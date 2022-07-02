import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
progress_board_path = dir_path.rsplit("/", 1)[0]
print("progress_board_path", progress_board_path)

sys.path.remove("/home/simon/git_workspace/ProgressBoard")

import pytest
import threading

from time import sleep
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from hyperactive import Hyperactive
from hyperactive_progress_board import ProgressBoard
from hyperactive_progress_board.progress_io import ProgressIO


def run_optimization():
    progress = ProgressBoard()

    @progress.update
    def model(opt):
        sleep(0.1)
        return -(opt["x1"] * opt["x1"] + opt["x2"] * opt["x2"])

    search_space = {
        "x1": list(range(-50, 50)),
        "x2": list(range(-50, 50)),
    }

    progress.open(show=False)

    hyper = Hyperactive()
    hyper.add_search(model, search_space, n_iter=150)
    hyper.run()


@pytest.fixture
def browser():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize ChromeDriver
    driver = Chrome()
    # Wait implicitly for elements to be ready before attempting interactions
    driver.implicitly_wait(10)

    # Return the driver object at the end of setup
    yield driver

    # For cleanup, quit the driver
    driver.quit()


def test_1(browser):
    print("\n browser \n", browser, "\n")

    run_opt = threading.Thread(target=run_optimization, name="run_optimization")
    run_opt.start()
    sleep(1)

    config_d = ProgressIO().read_config()

    URL = "http://localhost:5006/" + config_d["progress_ids"][0]
    print("\n URL \n", URL, "\n")
    browser.get(URL)

    plot0_xpath = "//div/descendant::canvas"
    plot2_xpath = (
        '//*[@id="afe38549-5e9a-4fd1-b0ec-991456b50807"]/div/div/div/div/svg[3]'
    )

    plot1_xpath = (
        '//*[@id="6cf6ad45-7e9c-4444-874c-f392e96e5483"]/div/div/div/div/svg[1]'
    )

    svg_xpath = "//*[name()='svg']"

    svg_obj_l = browser.find_elements_by_xpath(svg_xpath)
    assert len(svg_obj_l) == 6
