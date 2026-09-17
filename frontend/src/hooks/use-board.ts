import { useCallback, useEffect, useState } from "react";
import {
  httpTaskStore,
  type ColumnId,
  type NewTaskInput,
  type Task,
  type TaskEditInput,
  type TaskStore,
} from "@/lib/kanban";

export function useBoard(store: TaskStore = httpTaskStore) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [user, setUser] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    store
      .loadTasks()
      .then((loaded) => {
        if (!cancelled) setTasks(loaded);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load tasks");
      })
      .finally(() => {
        if (!cancelled) setReady(true);
      });
    setUser(store.loadUser());
    return () => {
      cancelled = true;
    };
  }, [store]);

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

  /** Create a new task, or save changes to an existing one, depending on
   * whether `id` matches a task already on the board. */
  const upsertTask = useCallback(
    (task: Omit<Task, "order"> & { order?: number }) => {
      const { id, order: _order, ...fields } = task;
      const editing = tasks.some((t) => t.id === id);

      const promise = editing
        ? store.updateTask(id, fields as TaskEditInput).then((updated) => {
            setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
          })
        : store.createTask(fields as NewTaskInput).then((created) => {
            setTasks((prev) => [...prev, created]);
          });

      promise.catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to save task"),
      );
    },
    [store, tasks],
  );

  const deleteTask = useCallback(
    (id: string) => {
      store
        .deleteTask(id)
        .then(() => setTasks((prev) => prev.filter((t) => t.id !== id)))
        .catch((err: unknown) =>
          setError(err instanceof Error ? err.message : "Failed to delete task"),
        );
    },
    [store],
  );

  /** Move a task to a column, inserting at `index` within that column. */
  const moveTask = useCallback(
    (id: string, status: ColumnId, index: number) => {
      store
        .moveTask(id, status, index)
        .then((updated) => setTasks(updated))
        .catch((err: unknown) =>
          setError(err instanceof Error ? err.message : "Failed to move task"),
        );
    },
    [store],
  );

  return { tasks, tasksIn, user, ready, error, joinBoard, upsertTask, deleteTask, moveTask };
}
