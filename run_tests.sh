#!/bin/bash

# copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

set -e

cd "$( dirname $0 )"

if [ -d htmlcov ]; then
  echo Removing old coverage report
  rm -fR htmlcov
fi

if which python3-coverage; then
  COVERAGE_BIN=python3-coverage
elif which coverage-3; then
  COVERAGE_BIN=coverage-3
else
  echo Could not find a python3-coverage binary to run tests
fi

if [ -n "$COVERAGE_BIN" ]; then
  echo Running coverage tests
  $COVERAGE_BIN run --source rebasedashdash -m pytest pytest/test*.py
  echo Generating code coverage report
  $COVERAGE_BIN html
  echo check directory htmlcov
  exit 0
fi

if which pytest; then
  PYTEST_BIN=pytest
elif which pytest-3; then
  PYTEST_BIN=pytest-3
else
  echo Could not find a pytest binary to run
  exit 1
fi

export PYTHONPATH=$PWD
$PYTEST_BIN pytest/test*.py
