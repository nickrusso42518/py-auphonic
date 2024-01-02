.DEFAULT_GOAL := test

.PHONY: test
test: clean lint conn run

.PHONY: ftest
ftest: clean lint conn

.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.py" | xargs pylint
	find . -name "*.py" | xargs black -l 84 --check
	@echo "Completed lint"

.PHONY: conn
conn:
	@echo "Starting  conn"
	python auphonic.py
	ls -l data_ref/
	@echo "Completed conn"

.PHONY: run
run:
	@echo "Starting  run"
	python produce.py
	tree test_files/
	@echo "Completed run"

.PHONY: clean
clean:
	@echo "Starting  clean"
	find . -name "*.pyc" | xargs rm
	rm -rf test_files/auphonic-results/
	@echo "Completed clean"
