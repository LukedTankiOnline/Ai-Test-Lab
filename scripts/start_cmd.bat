@echo off
REM Windows CMD helper to create venv, install minimal deps, and start the sandbox
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install --upgrade pip setuptools wheel
pip install -r requirements-minimal.txt
python -c "import nltk; nltk.download('wordnet')"
python -m uvicorn src.ai_test_lab.sandbox.main:app --reload --host 0.0.0.0 --port 8000
