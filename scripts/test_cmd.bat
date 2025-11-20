@echo off
REM Windows CMD helper to run tests
call .venv\Scripts\activate.bat 2>nul || echo ".venv activate not found; running pytest using current Python"
set PYTHONPATH=.;.\src
pytest -q
