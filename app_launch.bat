:: SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
:: SPDX-License-Identifier: MIT
::
:: Permission is hereby granted, free of charge, to any person obtaining a
:: copy of this software and associated documentation files (the "Software"),
:: to deal in the Software without restriction, including without limitation
:: the rights to use, copy, modify, merge, publish, distribute, sublicense,
:: and/or sell copies of the Software, and to permit persons to whom the
:: Software is furnished to do so, subject to the following conditions:
::
:: The above copyright notice and this permission notice shall be included in
:: all copies or substantial portions of the Software.
::
:: THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
:: IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
:: FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
:: THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
:: LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
:: FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
:: DEALINGS IN THE SOFTWARE.
:: edited by Ray Bernard , ray.bernard@outlook.com

@echo off
setlocal enabledelayedexpansion

set "env_path_found="

for /f "tokens=1,* delims= " %%a in ('"%localappdata%\NVIDIA\MiniConda\Scripts\conda.exe" env list') do (
    set "env_name=%%a"
    set "env_path=%%b"
    if "!env_path!"=="" (
        set "env_path=!env_name!"
    )
    echo !env_path! | findstr /C:"env_nvd_rag" > nul
    if !errorlevel! equ 0 (
        set "env_path_found=!env_path!"
        goto :endfor
    )
)

:endfor
@REM uncomment the blow lines to activate the OpenAI api locally
@REM please use the test_api.py to connect and play with model locally.
if not "%env_path_found%"=="" (
    echo Environment path found: %env_path_found%
    call "%localappdata%\NVIDIA\MiniConda\Scripts\activate.bat" %env_path_found%
    cd C:\Users\RayBe\AppData\Local\NVIDIA\ChatWithRTX\RAG\trt-llm-rag-windows-main
    python verify_install.py
    pip install -r requirements_api.txt 
    python app_sshtensortt.py
    @REM python app_api.py 
    @REM python test_api.py 

    pause
) else (
    echo Environment with 'env_nvd_rag' not found.
    pause
)

endlocal

