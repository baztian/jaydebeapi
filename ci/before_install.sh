#!/bin/bash
set -e

[ -n "$JYTHON" ] && "${TRAVIS_BUILD_DIR}/ci/before_install_jython.sh" || "${TRAVIS_BUILD_DIR}/ci/before_install_nonjython.sh"

if [ -f requirements.txt ]
then
    pip install -r requirements.txt
fi
