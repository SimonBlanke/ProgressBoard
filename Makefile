install:
	pip install .


reinstall:
	pip uninstall -y hyperactive_progress_board
	rm -fr build dist hyperactive_progress_board.egg-info
	python setup.py bdist_wheel
	pip install dist/*
