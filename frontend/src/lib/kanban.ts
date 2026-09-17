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

/**
 * Storage layer boundary.
 * Swap this implementation for a realtime / database backed store later —
 * the UI only depends on the TaskStore interface.
 */
export interface TaskStore {
  loadTasks(): Task[];
  saveTasks(tasks: Task[]): void;
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

export const localTaskStore: TaskStore = {
  loadTasks() {
    if (typeof window === "undefined") return seedTasks;
    try {
      const raw = window.localStorage.getItem(TASKS_KEY);
      if (!raw) return seedTasks;
      const parsed = JSON.parse(raw) as Task[];
      return Array.isArray(parsed) ? parsed : seedTasks;
    } catch {
      return seedTasks;
    }
  },
  saveTasks(tasks) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(TASKS_KEY, JSON.stringify(tasks));
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
