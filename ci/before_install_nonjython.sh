#!/bin/sh

cat requirements_python.txt >> requirements.txt
ln -s $VIRTUAL_ENV ~/myvirtualenv
