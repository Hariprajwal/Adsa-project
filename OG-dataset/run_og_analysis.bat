@echo off
REM ==============================================================================
REM   OG-DATASET ALGORITHM EVALUATION & FIGURE GENERATOR
REM   ADSA Course Project P9 - Entropy-Guided Hierarchical Load Balancing
REM ==============================================================================
title OG-Dataset Real HPC Workload Evaluator

echo ==============================================================================
echo    PROCESSING ALL 3 OFFICIAL SUPERCOMPUTING TRACES (CEA-Curie, LANL, LLNL)
echo ==============================================================================
echo.

cd /d "%~dp0"
python process_og_dataset.py --trace all --jobs 1500 --nodes 128

echo.
echo ==============================================================================
echo Processing complete for all three datasets! Check results in:
echo   - CEA-Curie:     OG-dataset\results\cea-curie\figures\
echo   - LANL-CM5:      OG-dataset\results\lanl\figures\
echo   - LLNL-Thunder:  OG-dataset\results\llnl\figures\
echo   - Master Report: OG-dataset\results\OG_ALL_DATASETS_REPORT.md
echo   - Unified CSV:   OG-dataset\results\og_all_datasets_comparison.csv
echo ==============================================================================
pause
