#!/usr/bin/env bash
mkdir refal
pushd refal
wget http://www.botik.ru/pub/local/scp/refal5/ref5_081222.zip
unzip ref5_081222.zip 
rm makefile
cp makefile.lin makefile
make
popd