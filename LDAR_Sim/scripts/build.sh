#!/bin/sh
rm -rf build
mkdir -p build/{inputs,sim_test,src} 
cd .. 
cp -r ./src/* scripts/build/src 
cp -r ./inputs/* scripts/build/inputs
cp -r ./sim_test/* scripts/build/sim_test
cd scripts 
pipenv requirements > requirements.txt
pip install -r requirements.txt --no-deps -t build
rm -f ldar-sim.zip
cd build
zip -r ../ldar-sim.zip . -i *
