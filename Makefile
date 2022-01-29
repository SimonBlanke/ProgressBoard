install:
	pip install .

reinstall:
	pip uninstall -y hyperactive_progress_board
	rm -fr build dist hyperactive_progress_board.egg-info
	python setup.py bdist_wheel
	pip install dist/*

test:
	python -m pytest -x -p no:warnings -rfEX tests/ \