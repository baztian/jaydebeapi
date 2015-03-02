#!/bin/bash
set -e

cat requirements-python.txt >> requirements.txt
ln -s $VIRTUAL_ENV $HOME/myvirtualenv
