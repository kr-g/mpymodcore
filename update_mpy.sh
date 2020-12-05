#!/bin/bash

pushd .

cd ../micropython
MPYHOME=$(pwd)
MPYVER=${1:-v1.13}

echo $MPYHOME $MPYVER

git checkout -f master

git pull

git checkout -f $MPYVER

cd $MPYHOME
git submodule update 

cd $MPYHOME/ports/unix
make submodules
make

cd $MPYHOME/mpy-cross
make 

popd 

echo
echo mpy-cross version
echo

../micropython/mpy-cross/mpy-cross --version

