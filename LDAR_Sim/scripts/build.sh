#!/bin/sh
rm -rf build
mkdir -p build 
cd build 
mkdir -p src 
mkdir -p inputs 
mkdir -p sim_test
cd .. 
cp ./src/* build/src
cp ./src/* build/inputs
cp ./src/* build/sim_test
pipenv lock -r > requirements.txt
pip install -r requirements.txt --no-deps -t build
rm -f ldar-sim.zip
cd build; zip -r ../ldar-sim.zip *
