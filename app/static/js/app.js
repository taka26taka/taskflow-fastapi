"use strict";
const $ = (selector) => document.querySelector(selector);
const editor = $("#editor"), form = $("#task-form"), deletion = $("#delete-dialog");
let currentId = null, deleteId = null, status = "all", loading = false, generation = 0;
const priorities = {high: "高", medium: "中", low: "低"};
async function api(path, options = {}) {
  const response = await fetch(path, {headers: {"Content-Type": "application/json"}, ...options});
  if (!response.ok) {
    if (response.status === 422) throw new Error("入力を確認してください。タイトルは1〜100文字、詳細は1000文字以内です。");
    if (response.status === 404) throw new Error("タスクが見つかりません。一覧を再読み込みしてください。");
    throw new Error("処理に失敗しました。時間をおいて再度お試しください。");
  }
  return response.status === 204 ? null : response.json();
}
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function dateTime(value) { return new Date(value).toLocaleString("ja-JP", {timeZone: "Asia/Tokyo", dateStyle:"short",timeStyle:"short"}); }
function showError(error) { $("#message").textContent = error.message; $("#message").className = "error"; }
function render(task) {
  const card = element("article", undefined, `task ${task.is_completed ? "done" : ""}`);
  const checkbox = document.createElement("input"); checkbox.type = "checkbox"; checkbox.checked = task.is_completed;
  checkbox.setAttribute("aria-label", `${task.title}を${task.is_completed ? "未完了" : "完了"}にする`);
  checkbox.addEventListener("change", async () => {
    checkbox.disabled = true;
    try { await api(`/api/tasks/${task.id}`, {method:"PATCH", body:JSON.stringify({is_completed:checkbox.checked})}); await load(); }
    catch (error) { checkbox.checked = task.is_completed; showError(error); }
    finally { checkbox.disabled = false; }
  });
  const content = element("div", undefined, "task-content"); content.append(element("h2", task.title));
  if (task.description) content.append(element("p", task.description, "description"));
  const meta = element("div", undefined, "meta");
  meta.append(element("span", `優先度 ${priorities[task.priority]}`, `badge ${task.priority}`));
  meta.append(element("span", task.is_completed ? "完了済み" : "未完了"));
  if (task.due_date) meta.append(element("span", `期限 ${task.due_date}${task.is_overdue ? " · 期限切れ" : ""}`, task.is_overdue ? "overdue" : ""));
  meta.append(element("span", `作成 ${dateTime(task.created_at)}`)); content.append(meta);
  const actions = element("div", undefined, "task-actions");
  const edit = element("button", "編集", "icon"); edit.setAttribute("aria-label", `${task.title}を編集`); edit.onclick = () => openEditor(task);
  const remove = element("button", "削除", "icon"); remove.setAttribute("aria-label", `${task.title}を削除`);
  remove.onclick = () => {deleteId = task.id; $("#delete-error").textContent = ""; deletion.showModal();};
  actions.append(edit, remove); card.append(checkbox, content, actions); return card;
}
async function load() {
  const requestGeneration = ++generation;
  loading = true; $("#tasks").setAttribute("aria-busy", "true"); $("#message").className = ""; $("#message").textContent = "読み込み中…";
  try {
    const [tasks, stats] = await Promise.all([api(`/api/tasks?status=${status}&sort=${$("#sort").value}`), api("/api/tasks/stats")]);
    if (requestGeneration !== generation) return;
    $("#tasks").replaceChildren(...tasks.map(render));
    for (const key of ["total","completed","pending","overdue"]) $(`#${key}`).textContent = stats[key];
    $("#empty").hidden = tasks.length !== 0; $("#message").textContent = `${tasks.length}件のタスク`;
  } catch (error) { if (requestGeneration === generation) showError(error); }
  finally { if (requestGeneration === generation) { loading = false; $("#tasks").setAttribute("aria-busy", "false"); } }
}
function openEditor(task = null) {
  form.reset(); currentId = task?.id ?? null; $("#form-error").textContent = "";
  $("#editor-title").textContent = task ? "タスクを編集" : "タスクを追加";
  if (task) for (const key of ["title","description","priority","due_date"]) form.elements.namedItem(key).value = task[key] ?? "";
  form.elements.namedItem("is_completed").checked = task?.is_completed ?? false;
  form.elements.namedItem("is_completed").closest("label").hidden = !task;
  editor.showModal(); form.elements.namedItem("title").focus();
}
$("#new-task").onclick = () => openEditor();
$("#close-editor").onclick = $("#cancel").onclick = () => editor.close();
form.addEventListener("submit", async event => {
  event.preventDefault(); $("#save").disabled = true; $("#form-error").textContent = "";
  const data = Object.fromEntries(new FormData(form)); data.title = data.title.trim(); data.due_date ||= null;
  delete data.is_completed;
  if (currentId !== null) data.is_completed = form.elements.namedItem("is_completed").checked;
  try { await api(currentId === null ? "/api/tasks" : `/api/tasks/${currentId}`, {method:currentId === null ? "POST" : "PATCH", body:JSON.stringify(data)}); editor.close(); await load(); }
  catch (error) { $("#form-error").textContent = error.message; }
  finally { $("#save").disabled = false; }
});
$("#keep").onclick = () => deletion.close();
$("#confirm-delete").onclick = async () => {
  $("#confirm-delete").disabled = true;
  try { await api(`/api/tasks/${deleteId}`, {method:"DELETE"}); deletion.close(); await load(); }
  catch (error) { $("#delete-error").textContent = error.message; }
  finally { $("#confirm-delete").disabled = false; }
};
document.querySelectorAll("[data-status]").forEach(button => button.onclick = async () => {
  if (loading) return; status = button.dataset.status;
  document.querySelectorAll("[data-status]").forEach(tab => tab.setAttribute("aria-pressed", String(tab === button))); await load();
});
$("#sort").onchange = () => load();
load();
