#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -rf jelly.wiki &> /dev/null
rm -rf jelly_prog &> /dev/null

out=0
git clone https://github.com/DennisMitchell/jelly.git "$DIR/jelly_prog"
EXITCODE=$?
if [ $EXITCODE -eq 0 ]; then
  echo "Clone of Jelly successful"
else
  echo "Clone of Jelly failed with exit code " $EXITCODE
  out=5
fi
git clone https://github.com/DennisMitchell/jelly.wiki.git "$DIR/jelly.wiki"
EXITCODE=$?
if [ $EXITCODE -eq 0 ]; then
  echo "Clone of Jelly wiki successful"
else
  echo "Clone of Jelly wiki failed with exit code " $EXITCODE
  out=7
fi

python3 token_descriptions.py

if [ $out -eq 0 ]; then
  echo "Setup successful"
else
  echo "Setup failed."
fi
exit $out
