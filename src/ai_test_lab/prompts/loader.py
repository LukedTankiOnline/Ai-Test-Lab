import yaml
from pathlib import Path
from typing import List, Dict, Any

def load_prompts(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open() as f:
        data = yaml.safe_load(f)
    # expect top-level list or dict of categories
    prompts = []
    if isinstance(data, dict):
        for cat, items in data.items():
            for it in items:
                prompts.append({"category": cat, **it})
    elif isinstance(data, list):
        prompts = data
    return prompts
