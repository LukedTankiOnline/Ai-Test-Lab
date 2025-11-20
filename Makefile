PYTHON=python
PIP=pip

.PHONY: install-minimal install-full start test clean

install-minimal:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && $(PIP) install --upgrade pip setuptools wheel && $(PIP) install -r requirements-minimal.txt

install-full:
	# On Debian/Ubuntu you may need system build tools first
	sudo apt-get update && sudo apt-get install -y build-essential python3-dev libssl-dev libffi-dev
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && $(PIP) install --upgrade pip setuptools wheel && $(PIP) install -r requirements-full.txt

start:
	. .venv/bin/activate && uvicorn src.ai_test_lab.sandbox.main:app --reload --host 0.0.0.0 --port 8000

test:
	# Ensure NLTK wordnet is present for semantic_fuzzer
	. .venv/bin/activate && $(PYTHON) -c "import nltk; nltk.download('wordnet')" || true
	PYTHONPATH=.:./src .venv/bin/pytest -q

clean:
	rm -rf .venv
