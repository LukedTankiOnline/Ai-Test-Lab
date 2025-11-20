# AI Test Lab

A modular testing lab to discover exploits, privacy risks, and side-channel vulnerabilities in LLMs and AI APIs.

Components:
- Model Interaction Sandbox: FastAPI app that accepts prompts, logs inputs/outputs/tokens/latency, and provides a simple dashboard.
- Prompt Fuzzer & Jailbreak Generator: CLI tool that mutates prompts (semantic drift, homoglyphs, contextual baiting).
- Side-Channel Traffic Analyzer: Scapy-based capture to analyze TLS packet sizes and timing and plot basic rate graphs.
- Red Team Prompt Library: `prompts/prompts.yaml` with categorized prompts and loader.
- Privacy Risk Simulator: Simulate sessions with fake sensitive data and diff outputs to test memorization/leakage.
- Exploit Dashboard: Simple HTML view served by the FastAPI app at `/dashboard`.

Getting started

Quick start (minimal demo)

1. Create a Python virtualenv and install the minimal runtime dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-minimal.txt
python -c "import nltk; nltk.download('wordnet')"
```

2. Run the sandbox (demo mode — uses simulated model if `OPENAI_API_KEY` is not set):

```bash
uvicorn src.ai_test_lab.sandbox.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/dashboard` to view logs and the dashboard.

Full install

If you want the full feature set (traffic analysis, clustering, and optional extras) install the full requirements which may need system build tools on some platforms:

```bash
# on Debian/Ubuntu you may need build tools first
sudo apt-get update && sudo apt-get install -y build-essential python3-dev libssl-dev libffi-dev
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -c "import nltk; nltk.download('wordnet')"
```

Then run the sandbox as above.

Fuzzer

```bash
python -m src.ai_test_lab.fuzzer.cli "Tell me a secret"
```

This writes `artifacts/fuzzed_prompts.json` by default. Use `--feed http://localhost:8000` to push mutated prompts into the sandbox.

Traffic analyzer

Requires root privileges to capture packets. Example:

```bash
sudo python -m src.ai_test_lab.traffic.analyzer --duration 30 --host api.openai.com
```

Advanced correlation:

You can correlate packet captures with logged prompts to visualize timing vs prompt topics. First capture packets to `artifacts/traffic.csv` (use the `--capture` flag) or provide an existing CSV. Then run:

```bash
# generate a correlation plot using the prompts saved in `artifacts/report.json` or a logs JSON
python -m src.ai_test_lab.traffic.analyzer --csv artifacts/traffic.csv --logs artifacts/report.json
```

The analyzer will produce `artifacts/traffic_correlation.png` which is embedded in the dashboard at `/dashboard` if present.

Privacy simulator

```python
from src.ai_test_lab.privacy.simulator import generate_sensitive_session, run_session_against_sandbox
sess = generate_sensitive_session()
res = run_session_against_sandbox(sess, sandbox_url='http://localhost:8000')
```

Ethics & safety

This toolbox is intended for internal security research and responsible red-teaming. Do not use it to attack third-party systems without explicit authorization. Follow applicable laws and ethics guidelines.

License

MIT-style (not included). Cite responsibly.
# CI and convenience

This repository includes a GitHub Actions workflow at `/.github/workflows/ci.yml` that runs the test suite on pushes and PRs for Python 3.11 and 3.12. The workflow installs required system build packages before installing `requirements-full.txt` so compiled extensions can build.

There is also a `Makefile` with convenient targets:

- `make install-minimal` — create a venv and install `requirements-minimal.txt` for a quick demo.
- `make install-full` — installs system build deps (Debian/Ubuntu example) and then installs `requirements-full.txt`.
- `make start` — run the FastAPI sandbox (assumes `.venv` activated by `install-*`).
- `make test` — run the test suite (ensures `wordnet` is available and runs `pytest`).

If you want CI to also publish releases or build packages, tell me and I will add a release workflow and `pyproject.toml` packaging metadata.
# Ai-Test-Lab