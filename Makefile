.DEFAULT_GOAL := test

.PHONY: test
test: clean lint run

.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.py" | xargs pylint
	find . -name "*.py" | xargs black -l 82 --check
	@echo "Completed lint"

.PHONY: run
run:
	@echo "Starting  run"
	python produce.py
	tree ~/Desktop/auphonic/
	@echo "Completed  run"

.PHONY: clean
clean:
	@echo "Starting  clean"
	find . -name "*.pyc" | xargs rm
	rm -rf ~/Desktop/auphonic/auphonic-results/
	@echo "Completed  clean"
