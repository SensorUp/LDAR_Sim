#!/bin/sh
rm -rf build
mkdir -p build 
cd build 
mkdir -p src 
mkdir -p inputs 
mkdir -p sim_test
cd .. 
cp -r ./src/. build/src 
cp ./inputs/* build/inputs
cp ./sim_test/* build/sim_test
pipenv lock -r > requirements.txt
pip install -r requirements.txt --no-deps -t build
rm -f ldar-sim.zip
cd build; zip -r ../ldar-sim.zip *
