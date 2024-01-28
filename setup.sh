#!/bin/bash

set -e

virtualenv --python=python3 env
source env/bin/activate
hash -r
pip install django==2.2
django-admin --version
