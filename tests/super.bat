@echo off
:: Forward execution to root super.bat
cd /d "%~dp0.."
call super.bat %*
