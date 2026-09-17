import { useState } from "react";
import type { ColumnId, Task } from "@/lib/kanban";
import { cn } from "@/lib/utils";
import { TaskCard } from "./TaskCard";

const accent: Record<ColumnId, string> = {
  todo: "bg-column-todo",
  "in-progress": "bg-column-progress",
  done: "bg-column-done",
};

interface Props {
  id: ColumnId;
  title: string;
  hint: string;
  tasks: Task[];
  draggingId: string | null;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onDragStart: (task: Task) => void;
  onDragEnd: () => void;
  onDrop: (status: ColumnId, index: number) => void;
}

export function BoardColumn({
  id,
  title,
  hint,
  tasks,
  draggingId,
  onEdit,
  onDelete,
  onDragStart,
  onDragEnd,
  onDrop,
}: Props) {
  const [overIndex, setOverIndex] = useState<number | null>(null);

  const handleOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = "move";
    setOverIndex(index);
  };

  const handleDrop = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.stopPropagation();
    setOverIndex(null);
    onDrop(id, index);
  };

  const indicator = (index: number) =>
    overIndex === index ? (
      <div className="my-1 h-0.5 rounded-full bg-ring/70 transition-all" />
    ) : null;

  return (
    <section
      onDragOver={(e) => handleOver(e, tasks.length)}
      onDragLeave={() => setOverIndex(null)}
      onDrop={(e) => handleDrop(e, tasks.length)}
      className={cn(
        "flex min-h-64 flex-col rounded-2xl border border-border bg-column p-3 transition-colors",
        overIndex !== null && "border-ring/40 bg-column-active",
      )}
      aria-label={title}
    >
      <header className="mb-3 flex items-center gap-2 px-1">
        <span className={cn("size-2 rounded-full", accent[id])} />
        <h2 className="text-sm font-semibold text-foreground">{title}</h2>
        <span className="rounded-full bg-secondary px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
          {tasks.length}
        </span>
        <span className="ml-auto hidden text-[11px] text-muted-foreground sm:block">{hint}</span>
      </header>

      <div className="flex flex-1 flex-col gap-2">
        {tasks.length === 0 && overIndex === null ? (
          <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-border/70 py-8 text-xs text-muted-foreground">
            No tasks yet
          </div>
        ) : null}

        {tasks.map((task, i) => (
          <div
            key={task.id}
            onDragOver={(e) => handleOver(e, i)}
            onDrop={(e) => handleDrop(e, i)}
          >
            {indicator(i)}
            <TaskCard
              task={task}
              dragging={draggingId === task.id}
              onEdit={onEdit}
              onDelete={onDelete}
              onDragStart={onDragStart}
              onDragEnd={onDragEnd}
            />
          </div>
        ))}
        {indicator(tasks.length)}
      </div>
    </section>
  );
}
