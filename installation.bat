@echo off
echo Installing Ai-Test-Lab (full requirements) on Windows
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
echo Installing Python packages (this may take a while)...
pip install -r requirements-full.txt
echo Downloading NLTK wordnet corpus (one-time)...
python -c "import nltk; nltk.download('wordnet')"
echo Installation complete.
echo Note: some packages (packet capture, pyshark) may require additional system components and admin privileges.
pause
