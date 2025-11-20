import argparse
import json
from pathlib import Path
import requests
from .mutators import (
    homoglyph_obfuscate,
    contextual_bait,
    semantic_drift,
    leet_transform,
    zero_width_insert,
    base64_encode,
    random_injection,
)

DEFAULT_STRATEGIES = [
    "original",
    "semantic_drift",
    "homoglyph",
    "contextual_bait",
    "leet",
    "zero_width",
    "base64",
    "injection",
]

def apply_strategy(prompt: str, strategy: str):
    if strategy == 'original':
        return prompt
    if strategy == 'semantic_drift':
        # return first variant
        return semantic_drift(prompt, n=1)[0]
    if strategy == 'homoglyph':
        return homoglyph_obfuscate(prompt)
    if strategy == 'contextual_bait':
        return contextual_bait(prompt)
    if strategy == 'leet':
        return leet_transform(prompt)
    if strategy == 'zero_width':
        return zero_width_insert(prompt)
    if strategy == 'base64':
        return base64_encode(prompt)
    if strategy == 'injection':
        return random_injection(prompt)
    return prompt


def mutate_and_save(prompt: str, out_path: Path, count: int = 10, feed_sandbox: str = None, strategies=None):
    strategies = strategies or DEFAULT_STRATEGIES
    results = []
    results.append({"type": "original", "prompt": prompt})
    i = 0
    # generate until count: cycle strategies, adding small random variations
    while len(results) < count and i < count * 3:
        strat = strategies[i % len(strategies)]
        mutated = apply_strategy(prompt, strat)
        # add slight randomization
        if strat == 'semantic_drift' and isinstance(mutated, list):
            mutated = mutated[0]
        results.append({"type": strat, "prompt": mutated})
        i += 1

    # ensure unique by prompt text
    seen = set()
    unique_results = []
    for r in results:
        if r['prompt'] in seen:
            continue
        seen.add(r['prompt'])
        unique_results.append(r)
        if len(unique_results) >= count:
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(unique_results, indent=2, ensure_ascii=False))

    if feed_sandbox:
        for r in unique_results:
            try:
                requests.post(feed_sandbox.rstrip('/') + '/api/send_prompt', json={"model":"simulated","prompt": r['prompt']}, timeout=10)
            except Exception as e:
                print(f"Warning: failed to feed sandbox: {e}")


def main():
    parser = argparse.ArgumentParser(description="Prompt Fuzzer & Jailbreak Generator")
    parser.add_argument('prompt', help='Input prompt to mutate')
    parser.add_argument('--out', '-o', default='artifacts/fuzzed_prompts.json')
    parser.add_argument('--count', '-n', type=int, default=12)
    parser.add_argument('--feed', help='Optional sandbox URL to feed mutated prompts, e.g. http://localhost:8000')
    parser.add_argument('--strategies', '-s', nargs='+', help='List of strategies to apply', default=None)
    args = parser.parse_args()
    strategies = args.strategies or DEFAULT_STRATEGIES
    mutate_and_save(args.prompt, Path(args.out), count=args.count, feed_sandbox=args.feed, strategies=strategies)


if __name__ == '__main__':
    main()
