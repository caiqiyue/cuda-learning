@echo off
REM ===========================================================================
REM  build_ggml_cuda.bat —— 用 CUDA 后端编译 ggml
REM
REM  用法（从仓库任意位置都可以）：
REM      cmd //c ggml-demo\build_ggml_cuda.bat [cuda_arch]
REM  默认 cuda_arch=89（Ada，如 RTX 4070 Ti SUPER / 4090 / 30 系）
REM  其他常见值：75(Turing)  80(Ampere)  86(Ampere)  89(Ada)  90(Hopper)
REM
REM  为什么必须单独写这个 bat：
REM    nvcc 在 Windows 上只接受 MSVC 作宿主编译器，不能用 MinGW 的 g++。
REM    而 VS 2019 生成器又要求装「CUDA VS 集成」组件（本机没装），
REM    所以走 vcvars64.bat + Ninja 这条路。
REM ===========================================================================
setlocal

set "CUDA_ARCH=%~1"
if "%CUDA_ARCH%"=="" set "CUDA_ARCH=89"

REM ---- CUDA Toolkit 位置，按需修改 ----
set "CUDA_ROOT=D:\Cuda"

REM ---- Visual Studio 2019 的 vcvars，按需修改 ----
set "VCVARS=%ProgramFiles(x86)%\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat"
if not exist "%VCVARS%" (
    echo [ERROR] 找不到 vcvars64.bat: %VCVARS%
    echo         请改这个脚本里的 VCVARS 变量，指向你机器上的 VS。
    exit /b 1
)
if not exist "%CUDA_ROOT%\bin\nvcc.exe" (
    echo [ERROR] 找不到 nvcc.exe: %CUDA_ROOT%\bin\nvcc.exe
    echo         请改这个脚本里的 CUDA_ROOT 变量。
    exit /b 1
)

REM ---- 仓库根目录（本脚本在 <repo>\ggml-demo\ 下）----
for %%I in ("%~dp0..") do set "REPO=%%~fI"

echo === CUDA arch      : %CUDA_ARCH%
echo === CUDA Toolkit   : %CUDA_ROOT%
echo === 仓库根目录      : %REPO%
echo.

call "%VCVARS%" || exit /b 1

cd /d "%REPO%" || exit /b 1

if exist "build\ggml-cuda" rmdir /s /q "build\ggml-cuda"

cmake -S ggml -B build/ggml-cuda -G Ninja ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_C_COMPILER=cl.exe ^
  -DCMAKE_CXX_COMPILER=cl.exe ^
  -DCMAKE_CUDA_COMPILER=%CUDA_ROOT%/bin/nvcc.exe ^
  -DCMAKE_CUDA_ARCHITECTURES=%CUDA_ARCH% ^
  -DGGML_CUDA=ON ^
  -DGGML_BUILD_EXAMPLES=ON ^
  -DGGML_BUILD_TESTS=OFF
if errorlevel 1 exit /b 1

echo === 编译中（CUDA 内核很多，第一次会比较久）===
cmake --build build/ggml-cuda --target mnist-eval mnist-train
if errorlevel 1 exit /b 1

echo.
echo === 完成，产物在 build\ggml-cuda\bin ===
dir /b "build\ggml-cuda\bin"
exit /b 0
