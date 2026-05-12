if (!getToken()) {
  window.location.href = "/login.html";
}

const noteForm = document.getElementById("note-form");
const formTitle = document.getElementById("form-title");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const notesList = document.getElementById("notes-list");
const emptyState = document.getElementById("empty-state");
const searchInput = document.getElementById("search-input");
const tagFilter = document.getElementById("tag-filter");
const userEmailEl = document.getElementById("user-email");
const logoutBtn = document.getElementById("logout-btn");

let editingNoteId = null;
let searchTimer;

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function parseTagInput(value) {
  return value
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

async function init() {
  try {
    const user = await api.me();
    userEmailEl.textContent = user.email;
    await Promise.all([refreshNotes(), refreshTagFilter()]);
  } catch {
    // apiFetch already handled the 401 redirect.
  }
}

async function refreshNotes() {
  const q = searchInput.value.trim();
  const tag = tagFilter.value;
  try {
    const notes = await api.listNotes(q, tag);
    renderNotes(notes);
  } catch (err) {
    console.error(err);
  }
}

async function refreshTagFilter() {
  const previous = tagFilter.value;
  try {
    const tags = await api.listTags();
    tagFilter.innerHTML = '<option value="">All tags</option>';
    for (const t of tags) {
      const option = document.createElement("option");
      option.value = t.name;
      option.textContent = t.name;
      tagFilter.appendChild(option);
    }
    tagFilter.value = previous;
  } catch (err) {
    console.error(err);
  }
}

function renderNotes(notes) {
  notesList.innerHTML = "";
  emptyState.classList.toggle("hidden", notes.length > 0);

  for (const note of notes) {
    const card = document.createElement("article");
    card.className = "note-card";
    card.innerHTML = `
      <h3>${escapeHtml(note.title)}</h3>
      <p class="note-content">${escapeHtml(note.content)}</p>
      <div class="tags">
        ${note.tags
          .map((t) => `<span class="tag">${escapeHtml(t.name)}</span>`)
          .join("")}
      </div>
      <div class="note-actions">
        <button type="button" class="btn-secondary" data-action="edit">Edit</button>
        <button type="button" class="btn-danger" data-action="delete">Delete</button>
      </div>
      <p class="meta">Updated ${new Date(note.updated_at).toLocaleString()}</p>
    `;
    card
      .querySelector('[data-action="edit"]')
      .addEventListener("click", () => startEdit(note));
    card
      .querySelector('[data-action="delete"]')
      .addEventListener("click", () => removeNote(note.id));
    notesList.appendChild(card);
  }
}

function startEdit(note) {
  editingNoteId = note.id;
  noteForm.title.value = note.title;
  noteForm.content.value = note.content;
  noteForm.tags.value = note.tags.map((t) => t.name).join(", ");
  formTitle.textContent = "Edit note";
  submitBtn.textContent = "Save changes";
  cancelBtn.classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  editingNoteId = null;
  noteForm.reset();
  formTitle.textContent = "New note";
  submitBtn.textContent = "Create";
  cancelBtn.classList.add("hidden");
}

async function removeNote(id) {
  if (!confirm("Delete this note?")) return;
  try {
    await api.deleteNote(id);
    if (editingNoteId === id) resetForm();
    await Promise.all([refreshNotes(), refreshTagFilter()]);
  } catch (err) {
    alert(err.message);
  }
}

noteForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = noteForm.title.value.trim();
  const content = noteForm.content.value;
  const tag_names = parseTagInput(noteForm.tags.value);
  if (!title) return;

  try {
    if (editingNoteId) {
      await api.updateNote(editingNoteId, { title, content, tag_names });
    } else {
      await api.createNote(title, content, tag_names);
    }
    resetForm();
    await Promise.all([refreshNotes(), refreshTagFilter()]);
  } catch (err) {
    alert(err.message);
  }
});

cancelBtn.addEventListener("click", resetForm);

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(refreshNotes, 300);
});

tagFilter.addEventListener("change", refreshNotes);

logoutBtn.addEventListener("click", () => {
  clearToken();
  window.location.href = "/login.html";
});

init();
