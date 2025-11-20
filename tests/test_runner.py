import json
from pathlib import Path
from src.ai_test_lab.runner import run_prompts

def test_run_prompts(tmp_path):
    out = tmp_path / 'report.json'
    rpt = run_prompts('prompts/prompts.yaml', out_report=str(out), do_fuzz=False)
    assert Path(rpt).exists()
    data = json.loads(Path(rpt).read_text())
    assert 'results' in data
    assert isinstance(data['results'], list)
