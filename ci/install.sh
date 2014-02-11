#!/bin/sh
set -e

pip install jip==0.7

install="${TRAVIS_BUILD_DIR}/ci/install_${BACKEND}.sh"
[ -x ${install} ] && ${install} || echo "nothing to run"
