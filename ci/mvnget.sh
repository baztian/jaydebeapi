#!/bin/bash
set -e

ARTIFACT_SPEC="$1"
GROUP_ID=${ARTIFACT_SPEC%%:*}
NON_GROUP_ID=${ARTIFACT_SPEC#*:}
ARTIFACT_NAME=`python -c "import re;print(re.search(r':(.*):', '$ARTIFACT_SPEC').group(1))"`
_PATH=${GROUP_ID/./\/}/$ARTIFACT_NAME
_ARTIFACT_SPEC_BASENAME=${NON_GROUP_ID/:/-}
VERSION=${ARTIFACT_SPEC##*:}
JAR=${_ARTIFACT_SPEC_BASENAME}.jar
if [ $# -ge 2 ]; then
    OUTPUT_DIR="$2"
else
    OUTPUT_DIR="./"
fi
JAR_FULL_PATH=${OUTPUT_DIR}/${_ARTIFACT_SPEC_BASENAME}.jar
if [ -f "$JAR_FULL_PATH" ]; then
    echo "File $JAR_FULL_PATH exists."
else
    echo "File $JAR_FULL_PATH does not exist. Start downloading .. "
    echo "Downloading ${ARTIFACT_NAME} version ${VERSION} group id ${GROUP_ID}..." >&2
    wget https://search.maven.org/remotecontent?filepath=${_PATH}/$VERSION/${_ARTIFACT_SPEC_BASENAME}.jar -O $JAR_FULL_PATH
    echo "...download of ${_ARTIFACT_SPEC_BASENAME}.jar finished." >&2
fi
