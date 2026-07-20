# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

from . import storage, llm, schemas

app = FastAPI(title="Email Productivity Agent")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ensure files exist at startup
@app.on_event("startup")
def startup():
    storage.ensure_files()

@app.post("/load_mock")
async def load_mock(payload: dict):
    existing = storage.read_jsonl("emails")
    existing_keys = {(e["sender"], e["subject"], e["body"]) for e in existing}

    incoming = payload.get("emails", [])
    added = 0
    next_id = storage.next_id(existing)

    for e in incoming:
        key = (e["sender"], e["subject"], e["body"])

        # ✔ Skip duplicates
        if key in existing_keys:
            continue

        obj = {
            "id": next_id,
            "sender": e["sender"],
            "recipient": e.get("recipient"),
            "subject": e["subject"],
            "body": e["body"],
            "timestamp": e["timestamp"],
            "raw": e
        }

        storage.append_jsonl("emails", obj)
        next_id += 1
        added += 1

    return {"loaded": added, "message": "Mock inbox updated"}


@app.get("/emails")
async def list_emails():
    return storage.read_jsonl("emails")



@app.post("/prompts")
async def add_prompt(p: schemas.PromptIn):
    prompts = storage.read_jsonl("prompts")

    # ✔ Skip duplicate prompt names
    for existing in prompts:
        if existing["name"].strip().lower() == p.name.strip().lower():
            return {"added": False, "message": "Prompt already exists", "prompt": existing}

    pid = storage.next_id(prompts)
    obj = {
        "id": pid,
        "name": p.name,
        "description": p.description,
        "template": p.template
    }
    storage.append_jsonl("prompts", obj)
    return {"added": True, "prompt": obj}


@app.get("/prompts")
async def get_prompts():
    return storage.read_jsonl("prompts")

@app.post("/process/{email_id}")
async def process_email(email_id: int):
    emails = storage.read_jsonl("emails")
    email = next((e for e in emails if e.get("id") == email_id), None)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    prompts = storage.read_jsonl("prompts")
    p_cat = next((p for p in prompts if "categorize" in (p.get("name") or "").lower()), None)
    p_task = next((p for p in prompts if "action" in (p.get("name") or "").lower()), None)
    if not p_cat or not p_task:
        raise HTTPException(status_code=400, detail="Required prompts missing")
    system1 = "You are an email classifier. Return a short category like Important, Newsletter, Spam, To-Do."
    user1 = p_cat.get("template","").replace("{subject}", email.get("subject","")).replace("{email_body}", email.get("body",""))
    cat_res = llm.call_llm(system1, user1)
    category = cat_res.get("text", "Unknown") if cat_res.get("success") else "Unknown"
    system2 = "You are an extractor. Return a JSON array of tasks."
    user2 = p_task.get("template","").replace("{subject}", email.get("subject","")).replace("{email_body}", email.get("body",""))
    act_res = llm.call_llm(system2, user2)
    actions = act_res.get("text", "[]") if act_res.get("success") else "[]"
    processed = storage.read_jsonl("processed")
    pid = storage.next_id(processed)
    obj = {
        "id": pid,
        "email_id": email_id,
        "category": category,
        "action_items_json": actions,
        "processed_at": datetime.utcnow().isoformat()
    }
    storage.append_jsonl("processed", obj)
    return {"category": category, "actions": actions}

@app.post("/agent/query")
async def agent_query(req: schemas.AgentRequest):
    emails = storage.read_jsonl("emails")
    email = next((e for e in emails if e.get("id") == req.email_id), None)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    prompts = storage.read_jsonl("prompts")
    sel = None
    if req.prompt_name:
        sel = next((p for p in prompts if p.get("name") == req.prompt_name), None)
    base = ""
    if sel:
        base = sel.get("template","").replace("{subject}", email.get("subject","")).replace("{email_body}", email.get("body",""))
    final = base + "\n\nUser instruction: " + (req.user_query or "")
    res = llm.call_llm("You are an email productivity assistant.", final)
    return res

@app.post("/draft")
async def create_draft(d: schemas.DraftIn):
    drafts = storage.read_jsonl("drafts")
    did = storage.next_id(drafts)
    obj = {
        "id": did,
        "email_id": d.email_id,
        "subject": d.subject,
        "body": d.body,
        "metadata_json": d.metadata_json,
        "saved_at": datetime.utcnow().isoformat()
    }
    storage.append_jsonl("drafts", obj)
    return obj

@app.get("/processed")
async def list_processed():
    return storage.read_jsonl("processed")

# -------------------------
# DRAFT ENDPOINTS (FULL CRUD)
# -------------------------

@app.get("/drafts")
async def list_drafts():
    return storage.read_jsonl("drafts")


@app.put("/draft/{draft_id}")
async def update_draft(draft_id: int, d: schemas.DraftIn):
    drafts = storage.read_jsonl("drafts")
    found = False
    updated = []

    for dr in drafts:
        if dr.get("id") == draft_id:
            found = True
            dr["subject"] = d.subject
            dr["body"] = d.body
            dr["metadata_json"] = d.metadata_json
        updated.append(dr)

    if not found:
        raise HTTPException(status_code=404, detail="Draft not found")

    storage.overwrite_jsonl("drafts", updated)
    return {"updated": draft_id}


@app.delete("/draft/{draft_id}")
async def delete_draft(draft_id: int):
    drafts = storage.read_jsonl("drafts")
    filtered = [d for d in drafts if d.get("id") != draft_id]

    if len(filtered) == len(drafts):
        raise HTTPException(status_code=404, detail="Draft not found")

    storage.overwrite_jsonl("drafts", filtered)
    return {"deleted": draft_id}

@app.post("/reset_all")
async def reset_all():
    storage.ensure_files(reset=True)  # you will update storage next
    return {"status": "ok", "message": "All data reset"}

@app.delete("/email/{email_id}")
async def delete_email(email_id: int):
    emails = storage.read_jsonl("emails")
    new_list = [e for e in emails if e.get("id") != email_id]
    storage.write_jsonl_full("emails", new_list)
    return {"deleted": email_id}

@app.delete("/delete_email/{email_id}")
async def delete_email(email_id: int):
    emails = storage.read_jsonl("emails")
    new_list = [e for e in emails if e.get("id") != email_id]
    storage.overwrite_jsonl("emails", new_list)

    # Also delete related processed entries
    processed = storage.read_jsonl("processed")
    new_processed = [p for p in processed if p.get("email_id") != email_id]
    storage.overwrite_jsonl("processed", new_processed)

    # Also delete drafts related to this email
    drafts = storage.read_jsonl("drafts")
    new_drafts = [d for d in drafts if d.get("email_id") != email_id]
    storage.overwrite_jsonl("drafts", new_drafts)

    return {"deleted": email_id, "message": "Email and related data removed"}
