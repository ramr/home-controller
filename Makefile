#!/usr/bin/env make

all:	build

clean:

build:	lint

test:	tests
tests:	lint unittests


lint:
	@echo "  - Linting README ..."
	@(markdownlint README.md || :)

	@echo "  - Linting python3 sources ..."
	python3 -m pylint *.py

	@echo "  - Linting shell scripts ..."
	shellcheck bin/*.sh


unittest:	unittests
unittests:


.PHONY:	clean build test tests lint unittest unittests
