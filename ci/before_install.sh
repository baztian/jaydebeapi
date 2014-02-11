#!/bin/sh

sudo apt-get update -qq
sudo apt-get install -qq openjdk-7-jdk openjdk-7-jre

before_install="${TRAVIS_BUILD_DIR}/ci/before_install_${BACKEND}.sh"
[ -x ${before_install} ] && ${before_install} || echo "nothing to run"
