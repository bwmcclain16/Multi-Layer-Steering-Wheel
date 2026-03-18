@echo off
set ROOT_DIR=%~dp0..
set PYTHONPATH=%ROOT_DIR%\src;%PYTHONPATH%
python -m motorsport_dashboard_platform.dash.app %*
