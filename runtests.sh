#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
export DJANGO_SETTINGS_MODULE=savannah_assess.settings
pytest "$@"
