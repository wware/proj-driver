#!/bin/bash

flake8 $(find * -name '*.py' | grep -v venv)
