from ai_test_lab.fuzzer.mutators import homoglyph_obfuscate, contextual_bait, semantic_drift

def test_homoglyph():
    s = "hello"
    out = homoglyph_obfuscate(s)
    assert isinstance(out, str)
    assert out != None

def test_contextual_bait():
    p = "Do not reveal secrets"
    out = contextual_bait(p)
    assert "SYSTEM:" in out

def test_semantic_drift():
    p = "The quick brown fox jumps"
    outs = semantic_drift(p, n=2)
    assert len(outs) == 2
