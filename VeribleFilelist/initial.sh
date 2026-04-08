#!/bin/bash

version=v0.0-3899-g75c38daf
if [ "$(uname -s)" = "Darwin" ]; then
    echo "MacOS"
    OS=macOS
    ext=tar.gz
elif [ "$(uname -s)" = "Linux" ]; then
    echo "Linux"
    OS=linux-static-x86_64
    ext=tar.gz
else
    echo "Windows"
    OS=win64
    ext=zip
fi
FILE_PATH="./verible/bin/verible-verilog-syntax"
if [ -f "$FILE_PATH" ]; then
    echo "Verible is already installed"
    exit 1
else
    wget https://github.com/chipsalliance/verible/releases/download/${version}/verible-${version}-${OS}.tar.gz
    tar -zxvf verible-${version}-${OS}.tar.gz
    rm verible-${version}-${OS}.tar.gz
    if [ "$(uname -s)" = "Darwin" ]; then
        mv verible-${version}-${OS} verible
    else
        mv verible-${version} verible
    fi
    touch ./verible/.version
    echo ${version} > ./verible/.version
fi
