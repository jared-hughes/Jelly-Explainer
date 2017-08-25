#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root (with sudo or su)"
  exit
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -r jelly.wiki &> /dev/null
rm -r jelly_prog &> /dev/null

out=0
git clone https://github.com/DennisMitchell/jelly.git "$DIR/jelly_prog"
EXITCODE=$?
if [ $EXITCODE -eq 0 ]; then
  echo "Clone of wiki successful"
else
  echo "Clone of wiki failed with exit code " $EXITCODE
  out=5
fi
git clone https://github.com/DennisMitchell/jelly.wiki.git "$DIR/jelly.wiki"
EXITCODE=$?
if [ $EXITCODE -eq 0 ]; then
  echo "Clone of wiki successful"
else
  echo "Clone of wiki failed with exit code " $EXITCODE
  out=7
fi
mv "$DIR/jelly_prog/jelly.py" "$DIR/jelly.py"
mv "$DIR/jelly_prog/dictionary.py" "$DIR/dictionary.py"

python3 token_descriptions.py

if [ $out -eq 0 ]; then
  echo "Setup successful"
else
  echo "Setup failed."
fi
exit $out
