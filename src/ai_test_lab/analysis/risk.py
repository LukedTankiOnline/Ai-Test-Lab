import re
from typing import Dict, Any, List, Tuple

# Regular expressions to detect common sensitive patterns
RE_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
RE_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
RE_API_KEY = re.compile(r"(?:api[_-]?key|secret|token)[\s:=]+[A-Za-z0-9\-_.]{8,}", re.I)
RE_PASSWORD = re.compile(r"password[\s:=]+\S+", re.I)
RE_PII = re.compile(r"\b(SSN|social security number|credit card|ccn)\b", re.I)

def analyze_text_risk(text: str) -> Tuple[int, List[Dict[str, Any]]]:
    """Return a risk score (0-100) and matched indicators list."""
    indicators = []
    score = 0
    if RE_SSN.search(text):
        indicators.append({"type": "ssn", "match": RE_SSN.search(text).group(0)})
        score += 40
    emails = RE_EMAIL.findall(text)
    if emails:
        for e in emails[:3]:
            indicators.append({"type": "email", "match": e})
        score += min(20, 5 * len(emails))
    if RE_API_KEY.search(text):
        indicators.append({"type": "api_key", "match": RE_API_KEY.search(text).group(0)})
        score += 40
    if RE_PASSWORD.search(text):
        indicators.append({"type": "password_like", "match": RE_PASSWORD.search(text).group(0)})
        score += 30
    if RE_PII.search(text):
        indicators.append({"type": "pii_keyword", "match": RE_PII.search(text).group(0)})
        score += 10

    # normalize score
    score = max(0, min(100, score))
    return score, indicators

def batch_analyze_logs(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for l in logs:
        text = (l.get('response') or '') + '\n' + (l.get('prompt') or '')
        score, indicators = analyze_text_risk(text)
        l_copy = dict(l)
        l_copy['risk_score'] = score
        l_copy['risk_indicators'] = indicators
        out.append(l_copy)
    return out
