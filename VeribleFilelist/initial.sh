#!/bin/bash

version=v0.0-3899-g75c38daf

FILE_PATH="./verible/bin/verible-verilog-syntax"
if [ -f "$FILE_PATH" ]; then
    echo "Verible is already installed"
    exit 1
else
    wget https://github.com/chipsalliance/verible/releases/download/${version}/verible-${version}-linux-static-x86_64.tar.gz
    tar -zxvf verible-${version}-linux-static-x86_64.tar.gz
    rm verible-${version}-linux-static-x86_64.tar.gz
    mv verible-${version} verible
    touch ./verible/.version
    echo ${version} > ./verible/.version
fi