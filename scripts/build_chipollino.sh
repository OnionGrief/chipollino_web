#!/usr/bin/env bash
pushd Chipollino
mkdir build
cd build
cmake ../.
cmake --build .
pushd ../refal
chmod +x compile.sh
./compile.sh
popd
popd