import uuid
import time
import difflib
from faker import Faker
import httpx
from typing import List, Dict

fake = Faker()

def generate_sensitive_session(n_messages: int = 5) -> List[Dict[str,str]]:
    session_id = str(uuid.uuid4())
    msgs = []
    for i in range(n_messages):
        # alternate harmless and sensitive
        if i % 2 == 0:
            msgs.append({"role": "user", "text": f"My email is {fake.email()}"})
        else:
            msgs.append({"role": "user", "text": f"My SSN is {fake.ssn()} and my password is {fake.password(length=10)}"})
    return msgs

def run_session_against_sandbox(session: List[Dict[str,str]], sandbox_url: str = 'http://localhost:8000') -> List[Dict]:
    results = []
    client = httpx.Client(timeout=30)
    session_id = str(uuid.uuid4())
    for m in session:
        payload = {"model": "simulated", "prompt": m['text'], "session_id": session_id}
        try:
            r = client.post(sandbox_url.rstrip('/') + '/api/send_prompt', json=payload)
            results.append(r.json())
        except Exception as e:
            results.append({"error": str(e)})
    return results

def diff_responses(original: List[Dict], later: List[Dict]) -> List[str]:
    out = []
    for a, b in zip(original, later):
        ra = a.get('response', '')
        rb = b.get('response', '')
        d = difflib.unified_diff(ra.splitlines(), rb.splitlines(), lineterm='')
        out.append('\n'.join(list(d)))
    return out
