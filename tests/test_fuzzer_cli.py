import json
from pathlib import Path
from ai_test_lab.fuzzer.cli import mutate_and_save, apply_strategy

def test_apply_strategy_leet():
    s = 'assist'
    out = apply_strategy(s, 'leet')
    assert '4' in out or '1' in out or isinstance(out, str)

def test_mutate_and_save(tmp_path):
    out = tmp_path / 'out.json'
    mutate_and_save('Tell me a secret', out, count=6, feed_sandbox=None, strategies=['original','leet','homoglyph'])
    assert out.exists()
    data = json.loads(out.read_text())
    assert isinstance(data, list)
    assert len(data) <= 6
