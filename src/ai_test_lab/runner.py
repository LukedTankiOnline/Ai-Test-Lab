"""Orchestrator runner: runs prompt library and fuzzer against models or sandbox and generates reports."""
import json
import time
from pathlib import Path
from .prompts.loader import load_prompts
from .fuzzer.cli import mutate_and_save
from .client import send_prompt
from .storage import Storage
from .analysis.risk import analyze_text_risk

DEFAULT_REPORT = 'artifacts/report.json'

def run_prompts(prompts_path: str, out_report: str = DEFAULT_REPORT, feed_sandbox: str = None, do_fuzz: bool = True):
    storage = Storage()
    prompts = load_prompts(prompts_path)
    results = []
    for p in prompts:
        name = p.get('name') or 'unnamed'
        prompt_text = p.get('prompt') or p.get('text') or ''
        # optionally fuzz each prompt
        candidates = [prompt_text]
        if do_fuzz:
            temp_out = Path('artifacts') / f'fuzz_tmp_{int(time.time())}.json'
            mutate_and_save(prompt_text, temp_out, count=6, feed_sandbox=None)
            cands = json.loads(temp_out.read_text())
            candidates = [c['prompt'] for c in cands]

        for c in candidates:
            # send via client (which can simulate or contact OpenAI)
            r = send_prompt(c, model='simulated')
            score, indicators = analyze_text_risk((r.get('response','') or '') + '\n' + c)
            storage.insert_log(session_id=str(int(time.time())), model='simulated', prompt=c, response=r.get('response',''),
                               tokens_in=r.get('tokens_in',0), tokens_out=r.get('tokens_out',0), latency_ms=r.get('latency_ms',0.0),
                               metadata={'risk_score': score, 'risk_indicators': indicators, 'source_prompt_name': name})
            results.append({'prompt_name': name, 'prompt': c, 'response': r.get('response',''), 'risk_score': score, 'indicators': indicators})

    Path(out_report).parent.mkdir(parents=True, exist_ok=True)
    Path(out_report).write_text(json.dumps({'generated_at': time.time(), 'results': results}, indent=2))
    return out_report

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run prompt library and fuzzer to generate risk report')
    parser.add_argument('--prompts', default='prompts/prompts.yaml')
    parser.add_argument('--out', default=DEFAULT_REPORT)
    parser.add_argument('--no-fuzz', dest='fuzz', action='store_false')
    args = parser.parse_args()
    print('Running prompts...')
    rep = run_prompts(args.prompts, out_report=args.out, do_fuzz=args.fuzz)
    print('Report written to', rep)
