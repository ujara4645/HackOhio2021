#!/usr/bin/env bash

mkdir -p debug/js debug/css debug/

cp -r static/* debug
elm make src/Main.elm --debug --output=debug/js/main.js
