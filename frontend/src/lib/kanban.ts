export type Priority = "low" | "medium" | "high";
export type ColumnId = "todo" | "in-progress" | "done";

export interface Task {
  id: string;
  title: string;
  description?: string;
  assignee?: string;
  priority: Priority;
  dueDate?: string; // ISO yyyy-mm-dd
  status: ColumnId;
  order: number;
}

export const COLUMNS: { id: ColumnId; title: string; hint: string }[] = [
  { id: "todo", title: "To Do", hint: "Not started" },
  { id: "in-progress", title: "In Progress", hint: "Being worked on" },
  { id: "done", title: "Done", hint: "Completed" },
];

export const PRIORITIES: { value: Priority; label: string }[] = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

/** Fields a new task needs. Mirrors openapi.yaml's TaskCreate. */
export interface NewTaskInput {
  title: string;
  description?: string;
  assignee?: string;
  priority: Priority;
  dueDate?: string;
  status: ColumnId;
}

/** Any subset of a task's editable fields. Mirrors openapi.yaml's TaskUpdate. */
export type TaskEditInput = Partial<NewTaskInput>;

/**
 * Storage layer boundary (docs/specs.md §16-17): the UI depends only on this
 * interface, never on how or where tasks are actually persisted, so the
 * implementation below can be swapped without touching components.
 *
 * Every operation here is async because the real implementation
 * (httpTaskStore) makes network calls; localTaskStore just wraps its
 * synchronous localStorage reads/writes in an already-resolved Promise so
 * both implementations satisfy the same interface.
 */
export interface TaskStore {
  loadTasks(): Promise<Task[]>;
  createTask(input: NewTaskInput): Promise<Task>;
  updateTask(id: string, input: TaskEditInput): Promise<Task>;
  deleteTask(id: string): Promise<void>;
  /** Move a task to `status`, inserting at `index` within that column. */
  moveTask(id: string, status: ColumnId, index: number): Promise<Task[]>;
  loadUser(): string | null;
  saveUser(name: string): void;
}

const TASKS_KEY = "team-kanban:tasks";
const USER_KEY = "team-kanban:user";

export const seedTasks: Task[] = [
  {
    id: "t1",
    title: "Draft onboarding checklist",
    description: "Outline the first-week steps for new teammates.",
    assignee: "Maria",
    priority: "high",
    dueDate: "2026-09-18",
    status: "todo",
    order: 0,
  },
  {
    id: "t2",
    title: "Collect feedback from pilot users",
    description: "Summarise the five interviews into key themes.",
    assignee: "Sam",
    priority: "medium",
    status: "todo",
    order: 1,
  },
  {
    id: "t3",
    title: "Rework board empty states",
    description: "Make them quieter and more helpful.",
    assignee: "Ines",
    priority: "low",
    status: "in-progress",
    order: 0,
  },
  {
    id: "t4",
    title: "Ship weekly release notes",
    description: "Publish the summary to the team channel.",
    assignee: "Theo",
    priority: "medium",
    dueDate: "2026-09-12",
    status: "done",
    order: 0,
  },
];

function readStoredTasks(): Task[] {
  if (typeof window === "undefined") return seedTasks;
  try {
    const raw = window.localStorage.getItem(TASKS_KEY);
    if (!raw) return seedTasks;
    const parsed = JSON.parse(raw) as Task[];
    return Array.isArray(parsed) ? parsed : seedTasks;
  } catch {
    return seedTasks;
  }
}

function writeStoredTasks(tasks: Task[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TASKS_KEY, JSON.stringify(tasks));
}

/** One past the highest existing order in `status` — the append-to-end rule
 * both stores use for a brand-new task or a task whose column just changed. */
function nextOrder(tasks: Task[], status: ColumnId, excludeId?: string): number {
  const orders = tasks.filter((t) => t.status === status && t.id !== excludeId).map((t) => t.order);
  return Math.max(-1, ...orders) + 1;
}

/**
 * localStorage-backed store. Kept as a fallback / offline implementation —
 * the app defaults to httpTaskStore below, backed by the real API described
 * in openapi.yaml.
 */
export const localTaskStore: TaskStore = {
  async loadTasks() {
    return readStoredTasks();
  },
  async createTask(input) {
    const tasks = readStoredTasks();
    const task: Task = { id: crypto.randomUUID(), order: nextOrder(tasks, input.status), ...input };
    writeStoredTasks([...tasks, task]);
    return task;
  },
  async updateTask(id, input) {
    const tasks = readStoredTasks();
    const existing = tasks.find((t) => t.id === id);
    if (!existing) throw new Error(`Task ${id} not found`);
    const statusChanged = input.status !== undefined && input.status !== existing.status;
    const order = statusChanged ? nextOrder(tasks, input.status!, id) : existing.order;
    const updated: Task = { ...existing, ...input, order };
    writeStoredTasks(tasks.map((t) => (t.id === id ? updated : t)));
    return updated;
  },
  async deleteTask(id) {
    writeStoredTasks(readStoredTasks().filter((t) => t.id !== id));
  },
  async moveTask(id, status, index) {
    const tasks = readStoredTasks();
    const moving = tasks.find((t) => t.id === id);
    if (!moving) throw new Error(`Task ${id} not found`);
    const column = tasks
      .filter((t) => t.status === status && t.id !== id)
      .sort((a, b) => a.order - b.order);
    const clamped = Math.max(0, Math.min(index, column.length));
    column.splice(clamped, 0, { ...moving, status });
    const reordered = new Map(column.map((t, i) => [t.id, i]));
    const next = tasks.map((t) =>
      reordered.has(t.id) ? { ...t, status, order: reordered.get(t.id)! } : t,
    );
    writeStoredTasks(next);
    return next;
  },
  loadUser() {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(USER_KEY);
  },
  saveUser(name) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(USER_KEY, name);
  },
};

// --- HTTP-backed store, talking to the backend described in openapi.yaml ---

const DEFAULT_API_BASE_URL = "http://localhost:8000";
const API_BASE_URL: string =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? DEFAULT_API_BASE_URL;

// The wire format spells the middle column with an underscore
// (docs/specs.md §27); this frontend's ColumnId spells it with a hyphen.
// httpTaskStore is the boundary that maps between the two — see
// openapi.yaml's info.description for why the mismatch exists.
const TO_WIRE_STATUS: Record<ColumnId, string> = {
  todo: "todo",
  "in-progress": "in_progress",
  done: "done",
};
const FROM_WIRE_STATUS: Record<string, ColumnId> = {
  todo: "todo",
  in_progress: "in-progress",
  done: "done",
};

interface WireTask {
  id: string;
  title: string;
  description?: string | null;
  assignee?: string | null;
  priority: Priority;
  dueDate?: string | null;
  status: string;
  order: number;
}

function fromWireTask(task: WireTask): Task {
  return {
    id: task.id,
    title: task.title,
    priority: task.priority,
    status: FROM_WIRE_STATUS[task.status] ?? (task.status as ColumnId),
    order: task.order,
    // exactOptionalPropertyTypes forbids assigning `undefined` to these —
    // omit the key entirely instead of setting it to null/undefined.
    ...(task.description != null ? { description: task.description } : {}),
    ...(task.assignee != null ? { assignee: task.assignee } : {}),
    ...(task.dueDate != null ? { dueDate: task.dueDate } : {}),
  };
}

function toWireBody(input: NewTaskInput | TaskEditInput): Record<string, unknown> {
  const { status, ...rest } = input;
  return status === undefined ? rest : { ...rest, status: TO_WIRE_STATUS[status] };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { message?: string };
      if (body.message) message = body.message;
    } catch {
      // Body wasn't JSON (or was empty) — fall back to the status line.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const httpTaskStore: TaskStore = {
  async loadTasks() {
    const tasks = await request<WireTask[]>("/tasks");
    return tasks.map(fromWireTask);
  },
  async createTask(input) {
    const task = await request<WireTask>("/tasks", {
      method: "POST",
      body: JSON.stringify(toWireBody(input)),
    });
    return fromWireTask(task);
  },
  async updateTask(id, input) {
    const task = await request<WireTask>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(toWireBody(input)),
    });
    return fromWireTask(task);
  },
  async deleteTask(id) {
    await request<void>(`/tasks/${id}`, { method: "DELETE" });
  },
  async moveTask(id, status, index) {
    const tasks = await request<WireTask[]>(`/tasks/${id}/move`, {
      method: "POST",
      body: JSON.stringify({ status: TO_WIRE_STATUS[status], index }),
    });
    return tasks.map(fromWireTask);
  },
  loadUser() {
    // Display name stays client-local: there is no backend user/account
    // concept to join (docs/specs.md §5.2; openapi.yaml's info.description).
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(USER_KEY);
  },
  saveUser(name) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(USER_KEY, name);
  },
};

export function formatDueDate(iso?: string) {
  if (!iso) return null;
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return null;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function initials(name?: string) {
  if (!name) return "?";
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? "")
    .join("");
}
