#!/bin/sh

poetry export -f requirements.txt --without-hashes --without-urls|sed 's/ *;.*//'
