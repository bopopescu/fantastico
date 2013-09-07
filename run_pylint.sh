#!/bin/bash

. pip-deps/bin/activate

pylint -f parseable --ignore=tests --max-line-length=130 --max-args=10 --disable=I0011,E1101,R0903,R0201,W0142,W0221,W0622 fantastico | tee pylint.out