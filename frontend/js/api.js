const TOKEN_KEY = "access_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let body = options.body;
  if (body && typeof body === "object" && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }

  const response = await fetch(path, { ...options, headers, body });

  if (response.status === 401 && !path.startsWith("/auth/")) {
    clearToken();
    window.location.href = "/login.html";
    throw new Error("Unauthorized");
  }
  return response;
}

async function readError(response) {
  try {
    const data = await response.json();
    if (Array.isArray(data.detail)) {
      return data.detail[0]?.msg || "Validation failed";
    }
    return data.detail || `Request failed (${response.status})`;
  } catch {
    return `Request failed (${response.status})`;
  }
}

const api = {
  async register(email, password) {
    const r = await apiFetch("/auth/register", {
      method: "POST",
      body: { email, password },
    });
    if (!r.ok) throw new Error(await readError(r));
    return r.json();
  },

  async login(email, password) {
    const form = new FormData();
    form.append("username", email);
    form.append("password", password);
    const r = await fetch("/auth/login", { method: "POST", body: form });
    if (!r.ok) throw new Error(await readError(r));
    return r.json();
  },

  async me() {
    const r = await apiFetch("/auth/me");
    if (!r.ok) throw new Error(await readError(r));
    return r.json();
  },

  async listNotes(q = "", tag = "") {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (tag) params.set("tag", tag);
    const qs = params.toString();
    const r = await apiFetch(`/notes${qs ? `?${qs}` : ""}`);
    if (!r.ok) throw new Error(await readError(r));
    return r.json();
  },

  async createNote(title, content, tag_names) {
    const r = await apiFetch("/notes", {
      method: "POST",
      body: { title, content, tag_names },
    });
    if (!r.ok) throw new Error(await readError(r));
    return r.json();
  },

  async updateNote(id, fields) {
    const r = await apiFetch(`/notes/${id}`, {
      method: "PATCH",
      body: fields,
    });
    if (!r.ok) throw new Error(await readError(r));
    return r.json();
  },

  async deleteNote(id) {
    const r = await apiFetch(`/notes/${id}`, { method: "DELETE" });
    if (!r.ok && r.status !== 204) throw new Error(await readError(r));
  },

  async listTags() {
    const r = await apiFetch("/tags");
    if (!r.ok) throw new Error(await readError(r));
    return r.json();
  },
};
