#!/usr/bin/env bash
set -euo pipefail
echo "Installing Ai-Test-Lab (full requirements) on Linux"
echo "Installing system build dependencies (Debian/Ubuntu example)"
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libssl-dev libffi-dev

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
echo "Installing Python packages (this may take a while)..."
pip install -r requirements-full.txt

echo "Downloading NLTK wordnet corpus (one-time)"
python -c "import nltk; nltk.download('wordnet')"

echo "Installation complete. Start the sandbox with: source .venv/bin/activate && python -m uvicorn src.ai_test_lab.sandbox.main:app --reload --host 0.0.0.0 --port 8000"
