#!/bin/sh -l

cd ./cli

env

python setup.py sdist bdist_wheel
ls ./dist

# These are set in the workflow/pypi.yml file
twine upload dist/* -u $INPUT_TWINE_USERNAME -p $INPUT_TWINE_PASSWORD
