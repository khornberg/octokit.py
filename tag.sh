#!/bin/bash

version=$(python setup.py --version)

if [ ! $(git tag -l "$version") ]; then
    git tag "$version"
fi
