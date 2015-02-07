#!/bin/bash
set -e

# JDK is not required for JPype1 anymore
# sudo apt-get update -qq
# sudo apt-get install -qq openjdk-7-jdk openjdk-7-jre

[ -n "$JYTHON" ] && "${TRAVIS_BUILD_DIR}/ci/before_install_jython.sh" || "${TRAVIS_BUILD_DIR}/ci/before_install_nonjython.sh"

if [ -f requirements.txt ]
then
    pip install -r requirements.txt
fi
