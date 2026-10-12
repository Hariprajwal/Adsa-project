@echo off
TITLE Entropy-Guided Cluster Video Streamer (ADSA P9)
COLOR 0B

echo ======================================================================
echo    ENTROPY-GUIDED HIERARCHICAL LOAD BALANCER AND VIDEO STREAMER
echo                    ADSA Project Engine (P9)
echo ======================================================================
echo.

:: Check Python installation
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.10+ and add it to your system PATH.
    pause
    exit /b 1
)

echo [1/3] Python environment verified.
echo [2/3] Checking dependencies...
python -c "import fastapi, uvicorn, multipart, websockets" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing missing requirements...
    pip install fastapi uvicorn python-multipart websockets
)

echo [3/3] Launching web server on http://127.0.0.1:8080 ...
echo.
echo ======================================================================
echo   Server is running at: http://127.0.0.1:8080
echo   Press CTRL+C in this terminal window to stop the server.
echo ======================================================================
echo.

:: Open browser after a brief delay once uvicorn binds to port 8080
start "" cmd /c "timeout /t 1 /nobreak >nul & start http://127.0.0.1:8080"

python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8080 --reload

pause
