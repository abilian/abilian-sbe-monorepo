#!/bin/sh

./poetry_requitements.sh > pip_requirements.txt
python diff_reqs_soft_vers.py ./pip_requirements.txt ./slapos_config/abilian-sbe/versions.cfg
