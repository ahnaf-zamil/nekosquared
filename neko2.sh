#!/bin/bash
which python3.6 || (echo "Python3.6 is not installed!"; exit 2)
[[ -f venv/bin/activate ]] && source venv/bin/activate && echo "Entered venv."
python3.6 -m neko2
exit ${?}
