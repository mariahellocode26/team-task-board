import { CalendarDays, Pencil, Trash2 } from "lucide-react";
import { formatDueDate, initials, type Task } from "@/lib/kanban";
import { cn } from "@/lib/utils";

const priorityClass: Record<Task["priority"], string> = {
  low: "bg-priority-low-soft text-priority-low",
  medium: "bg-priority-medium-soft text-priority-medium",
  high: "bg-priority-high-soft text-priority-high",
};

interface Props {
  task: Task;
  dragging: boolean;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onDragStart: (task: Task) => void;
  onDragEnd: () => void;
}

export function TaskCard({ task, dragging, onEdit, onDelete, onDragStart, onDragEnd }: Props) {
  const due = formatDueDate(task.dueDate);

  return (
    <article
      draggable
      onDragStart={(e) => {
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", task.id);
        onDragStart(task);
      }}
      onDragEnd={onDragEnd}
      onDoubleClick={() => onEdit(task)}
      className={cn(
        "group cursor-grab rounded-xl border border-border bg-card p-3.5 shadow-card transition-all duration-200",
        "hover:-translate-y-0.5 hover:border-ring/40 hover:shadow-card-hover active:cursor-grabbing",
        dragging && "rotate-[0.6deg] opacity-45",
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold leading-snug text-foreground">{task.title}</h3>
        <div className="flex shrink-0 gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
          <button
            type="button"
            aria-label={`Edit ${task.title}`}
            onClick={() => onEdit(task)}
            className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <Pencil className="size-3.5" />
          </button>
          <button
            type="button"
            aria-label={`Delete ${task.title}`}
            onClick={() => onDelete(task)}
            className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="size-3.5" />
          </button>
        </div>
      </div>

      {task.description ? (
        <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-muted-foreground">
          {task.description}
        </p>
      ) : null}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span
          className={cn(
            "rounded-full px-2 py-0.5 text-[11px] font-medium capitalize",
            priorityClass[task.priority],
          )}
        >
          {task.priority}
        </span>
        {due ? (
          <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground">
            <CalendarDays className="size-3" />
            {due}
          </span>
        ) : null}
        {task.assignee ? (
          <span className="ml-auto inline-flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <span className="grid size-6 place-items-center rounded-full bg-secondary text-[10px] font-semibold text-secondary-foreground">
              {initials(task.assignee)}
            </span>
            {task.assignee}
          </span>
        ) : null}
      </div>
    </article>
  );
}
