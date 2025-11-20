from ai_test_lab.analysis.risk import analyze_text_risk

def test_ssn_detection():
    txt = 'My SSN is 123-45-6789 and my email is test@example.com'
    score, inds = analyze_text_risk(txt)
    assert any(i['type']=='ssn' for i in inds)
    assert score >= 40

def test_email_detection():
    txt = 'Contact: hello@openai.com'
    score, inds = analyze_text_risk(txt)
    assert any(i['type']=='email' for i in inds)
