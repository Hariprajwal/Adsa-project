@echo off
setlocal EnableDelayedExpansion

TITLE Entropy-Guided Cluster Load Balancer ^& Data Suite (ADSA P9)
COLOR 0B

:: Ensure current working directory is always the project root
cd /d "%~dp0"
set "PROJECT_ROOT=%~dp0"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"

:: Ensure output_dataset and data/traces directories exist
if not exist "%PROJECT_ROOT%output_dataset" (
    mkdir "%PROJECT_ROOT%output_dataset" >nul 2>&1
)
if not exist "%PROJECT_ROOT%data\traces" (
    mkdir "%PROJECT_ROOT%data\traces" >nul 2>&1
)

:: Check for CLI Arguments (Non-interactive mode)
if not "%~1"=="" (
    if /i "%~1"=="1" goto ACTION_OPTION_1
    if /i "%~1"=="data" goto ACTION_OPTION_1
    if /i "%~1"=="official" goto ACTION_OPTION_1
    if /i "%~1"=="2" goto ACTION_OPTION_2
    if /i "%~1"=="run" goto ACTION_OPTION_2
    if /i "%~1"=="custom" goto ACTION_OPTION_2
    if /i "%~1"=="compare" goto ACTION_OPTION_2
    
    :: Fallback to running any script directly with PYTHONPATH pre-configured
    echo [EXEC] Running: python %* with project PYTHONPATH...
    python %*
    goto END_PROGRAM
)

:MAIN_MENU
cls
echo =========================================================================================
echo    ENTROPY-GUIDED HIERARCHICAL LOAD BALANCING AND VIDEO STREAMER
echo                         ADSA COURSE PROJECT (P9) - SUPER SUITE
echo =========================================================================================
echo  Project Root : %PROJECT_ROOT%
echo  Official Data: %PROJECT_ROOT%data\traces\
echo  Output Data  : %PROJECT_ROOT%output_dataset\
echo =========================================================================================
echo.
echo   [SELECT AN OPTION]:
echo.
echo     [1] Inspect Official HPC Dataset (ALL Jobs ^& 18-Column SWF Records)
echo         - Sourced from the Parallel Workloads Archive (LANL, LLNL, Curie)
echo         - Displays complete statistics ^& full SWF records for ALL 2,000 jobs
echo         - Dataset folder: data\traces\
echo.
echo     [2] Run Custom Algorithm vs. Round-Robin on ALL Jobs
echo         - Runs our proposed Entropy-Guided Hierarchical Balancer vs Round-Robin
echo         - Evaluates across ALL 2,000 supercomputing jobs
echo         - Computes Makespan, Load Variance, Tail Latency, and Fairness
echo         - Displays live side-by-side comparative table on screen
echo         - Exports results to output_dataset\tables\custom_vs_round_robin_comparison.csv
echo.
echo     [0] Exit
echo.
echo =========================================================================================
set /p "CHOICE=Enter choice (1, 2, or 0): "

if "%CHOICE%"=="1" goto MENU_OPTION_1
if "%CHOICE%"=="2" goto MENU_OPTION_2
if "%CHOICE%"=="0" goto EXIT_SCRIPT

echo.
echo [!] Invalid selection '%CHOICE%'. Please enter 1, 2, or 0.
timeout /t 2 >nul
goto MAIN_MENU


:: -------------------------------------------------------------------------------------------
:: OPTION 1: OPEN & INSPECT OFFICIAL HPC DATASET
:: -------------------------------------------------------------------------------------------

:ACTION_OPTION_1
:MENU_OPTION_1
cls
echo =========================================================================================
echo   [OPTION 1] OFFICIAL HPC DATASET INSPECTOR (PARALLEL WORKLOADS ARCHIVE)
echo =========================================================================================
echo.
python src\simulation\show_official_dataset.py
echo.
echo [i] Dataset files are saved in: %PROJECT_ROOT%data\traces\
echo.
if "%~1"=="" (
    pause
    goto MAIN_MENU
)
goto END_PROGRAM


:: -------------------------------------------------------------------------------------------
:: OPTION 2: RUN CUSTOM ALGORITHM VS ROUND-ROBIN
:: -------------------------------------------------------------------------------------------

:ACTION_OPTION_2
:MENU_OPTION_2
cls
echo =========================================================================================
echo   [OPTION 2] RUNNING CUSTOM PROPOSED ALGORITHM vs. ROUND-ROBIN BASELINE
echo =========================================================================================
echo.
python src\benchmark\run_custom_vs_round_robin.py
echo.
echo [i] Output results exported to: %PROJECT_ROOT%output_dataset\
echo.
if "%~1"=="" (
    pause
    goto MAIN_MENU
)
goto END_PROGRAM


:EXIT_SCRIPT
cls
echo Exiting super.bat. Have a great day!
exit /b 0

:END_PROGRAM
exit /b 0
