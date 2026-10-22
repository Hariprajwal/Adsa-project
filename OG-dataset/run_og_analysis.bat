@echo off
REM ==============================================================================
REM   OG-DATASET ALGORITHM EVALUATION & FIGURE GENERATOR
REM   ADSA Course Project P9 - Entropy-Guided Hierarchical Load Balancing
REM ==============================================================================
title OG-Dataset Real HPC Workload Evaluator

echo ==============================================================================
echo    PROCESSING ALGORITHMS ON REAL HPC TRACES (CEA-Curie, LANL, LLNL)
echo ==============================================================================
echo.

cd /d "%~dp0"
python process_og_dataset.py --trace cea-curie --jobs 1500 --nodes 128

echo.
echo ==============================================================================
echo Processing complete! Check figures in OG-dataset\results\figures\
echo ==============================================================================
pause
