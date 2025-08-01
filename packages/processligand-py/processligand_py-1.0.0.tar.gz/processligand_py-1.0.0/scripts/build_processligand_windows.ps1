git clone --depth 1 https://github.com/openbabel/openbabel.git
mkdir openbabel_build
cd openbabel_build

cmake ../openbabel `
        -DCMAKE_BUILD_TYPE=Release `
        -G Ninja `
        -DBUILD_SHARED=OFF `
        -DBUILD_GUI=OFF `
        -DCMAKE_BUILD_TYPE=Release `
        -DCMAKE_INSTALL_PREFIX="/project/openbabel-static" `
        -DPYTHON_BINDINGS=OFF `
        -DPERL_BINDINGS=OFF `
        -DRUBY_BINDINGS=OFF `
        -DCSHARP_BINDINGS=OFF `
        -DPTHREAD_LIBRARY="" `
        -DJAVA_BINDINGS=OFF `
        -DWITH_MAEPARSER=OFF `
        -DZLIB_LIBRARY=OFF `
        -DZLIB_INCLUDE_DIR=OFF

$coreCount = (Get-CimInstance -ClassName Win32_Processor).NumberOfLogicalProcessors
cmake --build . --config Release --target obabel -j $coreCount
cmake --build . --target install --config Release

cd ..
git clone -b cmake https://github.com/NRGlab/Process_Ligand
mkdir ProcessLigand_build
cd ProcessLigand_build

cmake ../Process_Ligand -DCMAKE_BUILD_TYPE=Release -DSTATIC_INSTALL_DIR="/project/openbabel-static" -DBUILD_STATIC_EXECUTABLE=ON -G Ninja
cmake --build . --target ProcessLigand --config Release