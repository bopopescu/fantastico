#!/bin/sh
pylint -f parseable --max-line-length=130 . | tee pylint.out