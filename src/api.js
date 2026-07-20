export const API_BASE = "https://emailagent-backend.onrender.com";


export async function fetchEmails() {
  const r = await fetch(`${API_BASE}/emails`);
  return r.json();
}

export async function loadMockInbox() {
  const data = await fetch("/mock_inbox.json").then(r => r.json());
  const r2 = await fetch(`${API_BASE}/load_mock`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(data)});
  return r2.json();
}

export async function loadPrompts() {
  const data = await fetch("/default_prompts.json").then(r => r.json());
  for (const p of data.prompts) {
    await fetch(`${API_BASE}/prompts`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(p)});
  }
  return {ok:true};
}

export async function processEmail(id) {
  const r = await fetch(`${API_BASE}/process/${id}`, {method:"POST"});
  return r.json();
}

export async function agentQuery(payload) {
  const r = await fetch(`${API_BASE}/agent/query`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(payload)});
  return r.json();
}

export async function createDraft(payload) {
  const r = await fetch(`${API_BASE}/draft`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(payload)});
  return r.json();
}

export async function listPrompts() {
  const r = await fetch(`${API_BASE}/prompts`);
  return r.json();
}

