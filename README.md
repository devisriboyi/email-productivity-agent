### Email Productivity Agent

A full-stack application that processes emails, categorizes them using LLM prompts, extracts action items, generates reply drafts, and provides an AI-powered chat interface. The system supports custom prompt configuration, full CRUD for drafts, inbox management, and a clean UI.

### Live URLs

***Frontend (Netlify):*** https://emailagentapp.netlify.app

***Backend (Render):*** https://emailagent-backend.onrender.com

---------

### Features

```
Email Ingestion

Load mock inbox (20 sample emails)

Prevents duplicates automatically

Delete individual emails

Reset all data

Prompt Management

Load default prompts (3 types)
````

------------

***Supports:***
```
Categorization prompt

Action-item extraction prompt

Auto-reply draft prompt

Email Processing

Categorizes each email using LLM

Extracts tasks as JSON

Stores processed results

Agent Chat

Ask questions about selected email

Prompt-driven responses

Customizable prompt selection

General instructions, summaries, action explanations

Draft Management (Full CRUD)

Create draft from any email

View list of drafts

Edit draft (subject + body)

Delete draft

All drafts persisted in drafts.jsonl
````

----------

### Tech Stack

***Frontend***

React (Vite)

JavaScript

Custom CSS

***Backend***

FastAPI

Uvicorn

Groq Llama 3.3

Pydantic

JSONL storage

-------------

### Deployment

***Backend:*** Render

***Frontend:*** Netlify

--------

***Backend Setup***
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
````

***Create .env file:***
```
GROQ_API_KEY=your_key_here
MODEL_NAME=llama-3.3-70b-versatile
````

***Run backend:***
```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
````

***Backend runs at:***

http://127.0.0.1:8000


***API docs:***

http://127.0.0.1:8000/docs

--------

***Frontend Setup***
```
cd frontend
npm install
npm run dev
````

Before running locally, set the API URL in api.js:
```
const API_BASE = "http://127.0.0.1:8000";
````

To build for Netlify:
```
npm run build
````

Upload dist/ folder to Netlify.

----------

### How to Use
***1. Load Mock Inbox***

Click Load Mock Inbox
→ 20 emails are inserted
→ duplicates are skipped

***2. Load Default Prompts***

Click Load Prompts
→ 3 prompts added automatically

***3. Process an Email***

Select email → Click Process Email
Backend performs:

Categorization

Action-item extraction

Saves results

***4. Use the Agent Chat***

Select email → Choose prompt → Ask question → Click Run Agent

***5. Create Draft***

Select email → Click Save Draft

***6. Edit Draft***

Go to Drafts panel → Click Edit → Change fields → Save Changes

***7. Delete Draft***

Click Delete next to any draft.

***8. Delete Email***

Click the X icon next to email.
Related:

Processed entries

Drafts
are also automatically deleted.

***9. Reset All Data***

Click Reset All
→ Clears emails, prompts, drafts, processed data.

-----------

### API Endpoints

***Emails***
```
GET    /emails
POST   /load_mock
DELETE /delete_email/{id}
POST   /reset_all
````

***Prompts***
```
GET  /prompts
POST /prompts
````

***Processing***
```
POST /process/{email_id}
POST /agent/query
````

***Drafts***
```
GET    /drafts
POST   /draft
PUT    /draft/{draft_id}
DELETE /draft/{draft_id}
````

-----------
***Folder-Based Data Storage***

***All data is stored in /data as JSONL files:***
```
emails.jsonl
prompts.jsonl
processed.jsonl
drafts.jsonl
````

No external DB required.

----------
### UI
<img width="1919" height="1199" alt="image" src="https://github.com/user-attachments/assets/6b05a378-7b12-430e-baba-0345f0ae5cba" />


-----------
### License

This Project is under MIT License

***email:*** eswarboyi7@gmail.com | Eswar Reddy Boyi

------------

***Notes***

The system never sends real emails; drafts are stored only.

All LLM behavior controlled via user-defined prompts.

Fully offline JSONL-based persistence.
