#!/bin/bash

ARTIFACT_SPEC=$1
GROUP_ID=${ARTIFACT_SPEC%%:*}
NON_GROUP_ID=${ARTIFACT_SPEC#*:}
ARTIFACT_NAME=`python -c "import re;print re.search(r':(.*):', '$ARTIFACT_SPEC').group(1)"`
_PATH=${GROUP_ID/./\/}/$ARTIFACT_NAME
_ARTIFACT_SPEC_BASENAME=${NON_GROUP_ID/:/-}
VERSION=${ARTIFACT_SPEC##*:}
echo "Downloading ${ARTIFACT_NAME} version ${VERSION} group id ${GROUP_ID}..." >&2
wget http://search.maven.org/remotecontent?filepath=${_PATH}/$VERSION/${_ARTIFACT_SPEC_BASENAME}.jar -O ${_ARTIFACT_SPEC_BASENAME}.jar
echo "...download of ${_ARTIFACT_SPEC_BASENAME}.jar finished." >&2
echo ${_ARTIFACT_SPEC_BASENAME}.jar
