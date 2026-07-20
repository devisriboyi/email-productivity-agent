import React, { useEffect, useState } from "react";

import {
  API_BASE,
  fetchEmails,
  loadMockInbox,
  loadPrompts,
  processEmail,
  agentQuery,
  createDraft,
  listPrompts,
} from "./api";

export default function App() {
  const [emails, setEmails] = useState([]);
  const [selected, setSelected] = useState(null);
  const [emailBody, setEmailBody] = useState("");
  const [output, setOutput] = useState("");
  const [prompts, setPrompts] = useState([]);
  const [promptChoice, setPromptChoice] = useState("");
  const [question, setQuestion] = useState("");
const [drafts, setDrafts] = useState([]);
const [editDraft, setEditDraft] = useState(null);

  async function refreshEmails() {
    const e = await fetchEmails();
    setEmails(Array.isArray(e) ? e : (e.emails || []));

  }

  useEffect(() => {
    refreshEmails();
    async function loadP() {
      const ps = await listPrompts();
      setPrompts(ps);
    }
    loadP();
  }, []);

  async function handleLoadMock() {
    const r = await loadMockInbox();
    setOutput(JSON.stringify(r, null, 2));
    await refreshEmails();
  }

  async function handleLoadPrompts() {
    await loadPrompts();
    const ps = await listPrompts();
    setPrompts(ps);
    setOutput("Prompts loaded");
  }

  async function handleSelect(id) {
    setSelected(id);
    const e = emails.find((x) => x.id === id);
    setEmailBody(e ? `${e.sender}\n${e.subject}\n\n${e.body}` : "");
  }

  async function handleProcess() {
    if (!selected) return setOutput("Select email");
    const res = await processEmail(selected);
    setOutput(JSON.stringify(res, null, 2));
    await refreshEmails();
  }

  async function handleAgent() {
    if (!selected) return setOutput("Select email");
    const payload = {
      email_id: selected,
      prompt_name: promptChoice || null,
      user_query: question,
    };
    const res = await agentQuery(payload);
    setOutput(JSON.stringify(res, null, 2));
  }

  async function handleCreateDraft() {
    if (!selected) return setOutput("Select email");
    const payload = {
      email_id: selected,
      subject: "Draft: " + selected,
      body: "Draft body",
      metadata_json: "{}",
    };
    const res = await createDraft(payload);
    setOutput(JSON.stringify(res, null, 2));
  }

  return (
    <div className="app-shell">
      
      {/* LEFT PANEL — INBOX */}
      <div className="inbox">
        <h3>Inbox</h3>
        <div className="controls">
          <button onClick={handleLoadMock}>Load Mock Inbox</button>
          <button 
  onClick={async ()=>{
    await fetch("https://emailagent-backend.onrender.com/reset_all", {method:"POST"});
    setOutput("All data reset");
    refreshEmails();
  }} 
  style={{marginLeft:8, background:"#ff4444", color:"#fff"}}
>
  Reset All
</button>

          <button onClick={handleLoadPrompts}>Load Prompts</button>
          <button onClick={refreshEmails}>Refresh</button>
        </div>

        <ul>
  {emails.map(e => (
    <li key={e.id} style={{ margin: "8px 0", display:"flex", alignItems:"center" }}>
      
      {/* DELETE BUTTON */}
      <button 
        style={{
          marginRight: 10,
          color: "white",
          background: "#d9534f",
          border: "none",
          borderRadius: 4,
          cursor: "pointer",
          padding: "2px 6px",
        }}
        onClick={async () => {
          await fetch(`https://emailagent-backend.onrender.com/delete_email/${e.id}`, { method: "DELETE" });
          await refreshEmails();
        }}
      >
        ✖
      </button>

      {/* EMAIL SELECT LINK */}
      <a 
        href="#" 
        onClick={(ev) => { ev.preventDefault(); handleSelect(e.id); }}
        style={{ textDecoration: "none" }}
      >
        {e.id} — {e.sender} — {e.subject}
      </a>
    </li>
  ))}
</ul>

      </div>


      {/* CENTER PANEL — EMAIL VIEWER */}
      <div className="viewer">
        <h3>Email Viewer</h3>

        <div className="card">
          <pre>{emailBody}</pre>
        </div>

        <div className="actions">
          <button className="primary" onClick={handleProcess}>
            Process Email
          </button>
          <button onClick={handleCreateDraft}>Save Draft</button>
        </div>
      </div>

      {/* RIGHT PANEL — AGENT */}
      <div className="agent">
        <h3>Agent Chat</h3>

        <div className="panel">
          <label>Prompt</label>
          <select
            value={promptChoice}
            onChange={(e) => setPromptChoice(e.target.value)}
          >
            <option value="">(none)</option>
            {prompts.map((p) => (
              <option key={p.id} value={p.name}>
                {p.name}
              </option>
            ))}
          </select>

          <div style={{ marginTop: 10 }}>
            <label>Question</label>
            <textarea
              rows={4}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </div>

          <div className="controls">
            <button className="primary" onClick={handleAgent}>
              Run Agent
            </button>
          </div>

          <h4 style={{ marginTop: 20 }}>Output</h4>
          <div className="output">
            <pre>{output}</pre>
          </div>
        </div>
      </div>
{/* RIGHT PANEL — DRAFTS */}
<div className="agent" style={{ width: "30%", padding: 22 }}>
  <h3>Drafts</h3>

  {/* Load Drafts */}
  <button
    onClick={async () => {
      const res = await fetch(`${API_BASE}/drafts`);
      const data = await res.json();
      setDrafts(data);
    }}
    style={{ marginBottom: 10 }}
  >
    Refresh Drafts
  </button>

  {/* List of drafts */}
  <ul style={{ listStyle: "none", padding: 0 }}>
    {drafts.map((d) => (
      <li key={d.id} style={{ marginBottom: 10 }}>
        <strong>{d.subject}</strong>

        {/* Edit button */}
        <button
          style={{ marginLeft: 10 }}
          onClick={() => setEditDraft(d)}
        >
          Edit
        </button>

        {/* Delete button */}
        <button
          style={{
            marginLeft: 10,
            background: "#ff4444",
            color: "white",
            border: "none",
            padding: "3px 7px",
            borderRadius: 4,
          }}
          onClick={async () => {
            await fetch(`${API_BASE}/draft/${d.id}`, {
              method: "DELETE",
            });
            const res = await fetch(`${API_BASE}/drafts`);
            setDrafts(await res.json());
          }}
        >
          Delete
        </button>
      </li>
    ))}
  </ul>

  {/* EDIT DRAFT MODAL */}
  {editDraft && (
    <div className="modal">
      <div className="modal-content">
        <h3>Edit Draft #{editDraft.id}</h3>

        <label>Subject</label>
        <input
          type="text"
          value={editDraft.subject}
          onChange={(e) =>
            setEditDraft({ ...editDraft, subject: e.target.value })
          }
        />

        <label style={{ marginTop: 10 }}>Body</label>
        <textarea
          rows={6}
          value={editDraft.body}
          onChange={(e) =>
            setEditDraft({ ...editDraft, body: e.target.value })
          }
        />

        <button
          className="primary"
          style={{ marginTop: 12 }}
          onClick={async () => {
            await fetch(`${API_BASE}/draft/${editDraft.id}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                subject: editDraft.subject,
                body: editDraft.body,
                metadata_json: editDraft.metadata_json || "{}",
                email_id: editDraft.email_id,
              }),
            });

            // reload drafts
            const r = await fetch(`${API_BASE}/drafts`);
            setDrafts(await r.json());

            setEditDraft(null);
          }}
        >
          Save Changes
        </button>

        <button
          style={{ marginTop: 10 }}
          onClick={() => setEditDraft(null)}
        >
          Close
        </button>
      </div>
    </div>
  )}
</div>


    </div>
  );
}
