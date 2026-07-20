# backend/app/storage.py
import json
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parents[1].parent  # backend/
DATA_DIR = BASE_DIR.parent / "data"  # project_root/data
DATA_DIR.mkdir(parents=True, exist_ok=True)

EMAILS_FILE = DATA_DIR / "emails.jsonl"
PROMPTS_FILE = DATA_DIR / "prompts.jsonl"
PROCESSED_FILE = DATA_DIR / "processed.jsonl"
DRAFTS_FILE = DATA_DIR / "drafts.jsonl"

def ensure_files(reset=False):
    for file in ["emails.jsonl", "prompts.jsonl", "processed.jsonl", "drafts.jsonl"]:
        p = get_path(file.replace(".jsonl", ""))
        if reset or not p.exists():
            p.write_text("")


def _read_jsonl_path(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    out = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out

def read_jsonl(fname: str) -> List[Dict[str, Any]]:
    mapping = {
        "emails": EMAILS_FILE,
        "prompts": PROMPTS_FILE,
        "processed": PROCESSED_FILE,
        "drafts": DRAFTS_FILE
    }
    p = mapping.get(fname)
    if p is None:
        raise ValueError("Unknown file")
    return _read_jsonl_path(p)

def append_jsonl(fname: str, item: Dict[str, Any]):
    mapping = {
        "emails": EMAILS_FILE,
        "prompts": PROMPTS_FILE,
        "processed": PROCESSED_FILE,
        "drafts": DRAFTS_FILE
    }
    p = mapping.get(fname)
    if p is None:
        raise ValueError("Unknown file")
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def overwrite_jsonl(fname: str, items: List[Dict[str, Any]]):
    mapping = {
        "emails": EMAILS_FILE,
        "prompts": PROMPTS_FILE,
        "processed": PROCESSED_FILE,
        "drafts": DRAFTS_FILE
    }
    p = mapping.get(fname)
    if p is None:
        raise ValueError("Unknown file")
    with p.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

def next_id(items: List[dict]) -> int:
    if not items:
        return 1
    return max((it.get("id", 0) for it in items), default=0) + 1

def write_jsonl_full(name, items):
    p = get_path(name)
    with p.open("w") as f:
        for o in items:
            f.write(json.dumps(o) + "\n")

def get_path(name: str) -> Path:
    mapping = {
        "emails": EMAILS_FILE,
        "prompts": PROMPTS_FILE,
        "processed": PROCESSED_FILE,
        "drafts": DRAFTS_FILE
    }
    return mapping.get(name)
