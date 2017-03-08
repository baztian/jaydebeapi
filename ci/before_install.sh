#!/bin/sh
set -e

[ -n "$JYTHON" ] && "${TRAVIS_BUILD_DIR}/ci/before_install_jython.sh" || true
