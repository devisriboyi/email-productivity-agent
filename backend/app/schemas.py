# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmailIn(BaseModel):
    sender: str
    recipient: Optional[str] = None
    subject: str
    body: str
    timestamp: datetime

class PromptIn(BaseModel):
    name: str
    description: Optional[str] = None
    template: str

class DraftIn(BaseModel):
    email_id: Optional[int] = None
    subject: str
    body: str
    metadata_json: Optional[str] = None

class AgentRequest(BaseModel):
    email_id: int
    prompt_name: Optional[str] = None
    user_query: Optional[str] = None
