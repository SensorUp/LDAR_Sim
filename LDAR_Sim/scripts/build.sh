#!/bin/sh
rm -rf build
mkdir -p build 
cd build 
mkdir -p src 
mkdir -p inputs 
mkdir -p sim_test
cd .. 
<<<<<<< HEAD
cp -r ./src/. build/src 
=======
cp ./src/*.py build/src
>>>>>>> 7c5e5a4d2d94998a0db16c0c4af2ac0cf526da59
cp ./inputs/* build/inputs
cp ./sim_test/* build/sim_test
pipenv lock -r > requirements.txt
pip install -r requirements.txt --no-deps -t build
rm -f ldar-sim.zip
<<<<<<< HEAD
cd build; zip -r ../ldar-sim.zip *
=======
cd build; zip -r ../ldar-sim.zip *
>>>>>>> 7c5e5a4d2d94998a0db16c0c4af2ac0cf526da59
