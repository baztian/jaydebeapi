#!/bin/sh
pip install jip==0.7

install="${TRAVIS_BUILD_DIR}/ci/install_${BACKEND}.sh"
[ -x ${install} ] && ${install} || echo "nothing to run"
