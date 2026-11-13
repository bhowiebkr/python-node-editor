#!/bin/sh
# Start the node editor with the Python in the "venv" folder.
# Make the venv first. See "Quick start" in README.md.
cd "$(dirname "$0")" || exit 1

if [ ! -x venv/bin/python ]; then
    echo 'The venv folder was not found. See "Quick start" in README.md.'
    exit 1
fi

exec venv/bin/python main.py
