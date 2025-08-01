#!/bin/bash
set -e
STATIC_INSTALL_DIR=../openbabel-static
git clone --depth 1 https://github.com/ThomasDesc/openbabel
mkdir openbabel_build
cd openbabel_build
cmake ../openbabel \
        -DBUILD_SHARED=OFF \
        -DBUILD_GUI=OFF \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=$STATIC_INSTALL_DIR \
        -DPYTHON_BINDINGS=OFF \
        -DPERL_BINDINGS=OFF \
        -DRUBY_BINDINGS=OFF \
        -DCSHARP_BINDINGS=OFF \
        -DJAVA_BINDINGS=OFF \
        -DPTHREAD_LIBRARY="" \
        -DWITH_MAEPARSER=OFF \
        -DZLIB_LIBRARY=OFF \
        -DZLIB_INCLUDE_DIR=OFF \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
        -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" \
        -DCMAKE_OSX_DEPLOYMENT_TARGET=10.9
cmake --build . --config Release --target obabel -j "$(sysctl -n hw.ncpu)"
cmake --build . --target install

cd ..
git clone -b cmake https://github.com/NRGlab/Process_Ligand
mkdir ProcessLigand_build
cd ProcessLigand_build
cmake ../Process_Ligand \
          -DCMAKE_BUILD_TYPE=Release \
          -DSTATIC_INSTALL_DIR=$STATIC_INSTALL_DIR \
          -DBUILD_STATIC_EXECUTABLE=OFF \
          -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" \
          -DCMAKE_OSX_DEPLOYMENT_TARGET=10.9
make -j "$(sysctl -n hw.ncpu)"
