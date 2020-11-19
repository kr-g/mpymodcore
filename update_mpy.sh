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
git submodule update #--init

cd $MPYHOME/ports/unix
make V=1
#make deplibs

cd $MPYHOME/mpy-cross
make V=1

popd 

echo
echo mpy-cross version
echo

../micropython/mpy-cross/mpy-cross --version

