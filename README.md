# Jelly-Explainer
Aims to make an automated explainer for programs in Dennis Mitchell's esoteric language Jelly.

This is VERY MUCH a work in progress right now

- - - - -

# SETUP

  1. Run setup.sh as root
      sudo bash setup.sh
  2. Done setting up!

# USAGE

There is not a proper interface yet, but you can use the program by running named_parsing.py with python3. Run the code `explain(test_string)`, where `test_string` is the program you want to explain.

# Troubleshooting

If you an error which states `encoding not declared`, add the line `#-*- encoding:utf-8 -*-` to the top of all files in question.
