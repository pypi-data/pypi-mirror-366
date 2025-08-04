#!/bin/bash
set -e  # exit if an error occurs

BUILD_PATH="build/`dev/build/abi.py`"

echo Cleaning $BUILD_PATH...
meson compile -C $BUILD_PATH --clean

