// Task Tracker frontend (baseline). Talks to the FastAPI backend.
const API = "http://localhost:8000";

const COLUMNS = [
  { key: "todo", label: "To do" },
  { key: "in_progress", label: "In progress" },
  { key: "done", label: "Done" },
];

const board = document.getElementById("board");
const backdrop = document.getElementById("modal-backdrop");
const form = document.getElementById("task-form");
const formError = document.getElementById("form-error");
const modalTitle = document.getElementById("modal-title");

// Current query filters (extended by features).
const filters = {};

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.status === 204 ? null : res.json();
}

function buildQuery() {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== null && v !== "") params.set(k, v);
  }
  const q = params.toString();
  return q ? `?${q}` : "";
}

async function loadBoard() {
  let tasks = [];
  try {
    tasks = await api("/tasks" + buildQuery());
  } catch (e) {
    board.innerHTML = `<p class="error">Cannot reach API at ${API}. Is the backend running?</p>`;
    return;
  }
  render(tasks);
}

function render(tasks) {
  board.innerHTML = "";
  for (const col of COLUMNS) {
    const inCol = tasks.filter((t) => t.status === col.key);
    const el = document.createElement("section");
    el.className = "column";
    el.innerHTML = `<h2>${col.label} <span>${inCol.length}</span></h2>`;
    if (inCol.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "No tasks";
      el.appendChild(empty);
    }
    for (const t of inCol) el.appendChild(cardEl(t));
    board.appendChild(el);
  }
}

function cardEl(t) {
  const card = document.createElement("div");
  card.className = `card prio-${t.priority}`;
  card.onclick = () => openModal(t);

  const parts = [`<div class="title">${escapeHtml(t.title)}</div>`];
  if (t.description) parts.push(`<div class="desc">${escapeHtml(t.description)}</div>`);

  const meta = [`<span class="pill">${t.priority}</span>`];
  if (t.assignee) meta.push(`<span class="pill assignee">${escapeHtml(t.assignee)}</span>`);
  // Feature hooks append extra meta here (see cardExtras).
  meta.push(...cardExtras(t));
  parts.push(`<div class="meta">${meta.join("")}</div>`);

  card.innerHTML = parts.join("");
  return card;
}

// Due dates + tags (mid-course project): pills/chips shown on each card.
function cardExtras(t) {
  const extras = [];
  if (t.due_date) {
    const cls = t.overdue ? "pill overdue" : "pill due-date";
    const label = t.overdue ? "Overdue " : "Due ";
    extras.push(`<span class="${cls}">${label}${escapeHtml(t.due_date)}</span>`);
  }
  for (const tag of t.tags || []) {
    extras.push(`<span class="pill tag">${escapeHtml(tag)}</span>`);
  }
  return extras;
}

// Due dates + tags: inject the two extra inputs into the modal form.
function renderFeatureFields(t) {
  const container = document.getElementById("feature-fields");
  container.innerHTML = `
    <label>Due date
      <input id="f-due-date" type="date" />
    </label>
    <label>Tags <span class="hint">(comma-separated)</span>
      <input id="f-tags" type="text" placeholder="e.g. backend, urgent" />
    </label>
  `;
  document.getElementById("f-due-date").value = (t && t.due_date) || "";
  document.getElementById("f-tags").value = t && t.tags ? t.tags.join(", ") : "";
}

function collectFeatureFields(payload) {
  const due = document.getElementById("f-due-date").value;
  payload.due_date = due || null;
  const tagsRaw = document.getElementById("f-tags").value;
  payload.tags = tagsRaw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function openModal(task = null) {
  formError.hidden = true;
  form.reset();
  document.getElementById("task-id").value = task ? task.id : "";
  modalTitle.textContent = task ? "Edit task" : "New task";
  if (task) {
    document.getElementById("f-title").value = task.title;
    document.getElementById("f-description").value = task.description || "";
    document.getElementById("f-status").value = task.status;
    document.getElementById("f-priority").value = task.priority;
    document.getElementById("f-assignee").value = task.assignee || "";
  }
  renderFeatureFields(task);
  ensureDeleteButton(task);
  backdrop.hidden = false;
}

function ensureDeleteButton(task) {
  const existing = document.getElementById("delete-btn");
  if (existing) existing.remove();
  if (!task) return;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.id = "delete-btn";
  btn.className = "btn";
  btn.textContent = "Delete";
  btn.onclick = async () => {
    await api(`/tasks/${task.id}`, { method: "DELETE" });
    closeModal();
    loadBoard();
  };
  document.querySelector(".modal-actions").prepend(btn);
}

function closeModal() {
  backdrop.hidden = true;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.hidden = true;
  const id = document.getElementById("task-id").value;
  const payload = {
    title: document.getElementById("f-title").value,
    description: document.getElementById("f-description").value,
    status: document.getElementById("f-status").value,
    priority: document.getElementById("f-priority").value,
    assignee: document.getElementById("f-assignee").value,
  };
  collectFeatureFields(payload);
  try {
    if (id) {
      await api(`/tasks/${id}`, { method: "PUT", body: JSON.stringify(payload) });
    } else {
      await api("/tasks", { method: "POST", body: JSON.stringify(payload) });
    }
    closeModal();
    loadBoard();
  } catch (err) {
    formError.textContent = err.message;
    formError.hidden = false;
  }
});

document.getElementById("new-task-btn").onclick = () => openModal();
document.getElementById("cancel-btn").onclick = closeModal;
backdrop.addEventListener("click", (e) => { if (e.target === backdrop) closeModal(); });

// Toolbar filters: tag search + overdue-only toggle.
let tagFilterTimer;
document.getElementById("tag-filter").addEventListener("input", (e) => {
  clearTimeout(tagFilterTimer);
  const value = e.target.value.trim();
  tagFilterTimer = setTimeout(() => {
    filters.tag = value || undefined;
    loadBoard();
  }, 200);
});
document.getElementById("overdue-filter").addEventListener("change", (e) => {
  filters.overdue = e.target.checked ? "true" : undefined;
  loadBoard();
});

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

loadBoard();
