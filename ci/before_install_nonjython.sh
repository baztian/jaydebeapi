#!/bin/bash
set -e

cat requirements_python.txt >> requirements.txt
ln -s $VIRTUAL_ENV $HOME/myvirtualenv
