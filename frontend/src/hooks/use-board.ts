import { useCallback, useEffect, useState } from "react";
import {
  localTaskStore,
  type ColumnId,
  type Task,
  type TaskStore,
} from "@/lib/kanban";

export function useBoard(store: TaskStore = localTaskStore) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [user, setUser] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setTasks(store.loadTasks());
    setUser(store.loadUser());
    setReady(true);
  }, [store]);

  useEffect(() => {
    if (ready) store.saveTasks(tasks);
  }, [tasks, ready, store]);

  const joinBoard = useCallback(
    (name: string) => {
      store.saveUser(name);
      setUser(name);
    },
    [store],
  );

  const tasksIn = useCallback(
    (status: ColumnId) =>
      tasks.filter((t) => t.status === status).sort((a, b) => a.order - b.order),
    [tasks],
  );

  const upsertTask = useCallback((task: Omit<Task, "order"> & { order?: number }) => {
    setTasks((prev) => {
      const existing = prev.find((t) => t.id === task.id);
      if (existing) {
        const statusChanged = existing.status !== task.status;
        const order = statusChanged
          ? Math.max(-1, ...prev.filter((t) => t.status === task.status).map((t) => t.order)) + 1
          : existing.order;
        return prev.map((t) => (t.id === task.id ? { ...t, ...task, order } : t));
      }
      const order =
        Math.max(-1, ...prev.filter((t) => t.status === task.status).map((t) => t.order)) + 1;
      return [...prev, { ...task, order } as Task];
    });
  }, []);

  const deleteTask = useCallback((id: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== id));
  }, []);

  /** Move a task to a column, inserting at `index` within that column. */
  const moveTask = useCallback((id: string, status: ColumnId, index: number) => {
    setTasks((prev) => {
      const moving = prev.find((t) => t.id === id);
      if (!moving) return prev;
      const column = prev
        .filter((t) => t.status === status && t.id !== id)
        .sort((a, b) => a.order - b.order);
      const clamped = Math.max(0, Math.min(index, column.length));
      column.splice(clamped, 0, { ...moving, status });
      const reordered = new Map(column.map((t, i) => [t.id, i]));
      return prev.map((t) =>
        reordered.has(t.id) ? { ...t, status, order: reordered.get(t.id)! } : t,
      );
    });
  }, []);

  return { tasks, tasksIn, user, ready, joinBoard, upsertTask, deleteTask, moveTask };
}
