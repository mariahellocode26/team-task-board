import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { BoardColumn } from "@/components/kanban/BoardColumn";
import { TaskDialog } from "@/components/kanban/TaskDialog";
import { JoinDialog } from "@/components/kanban/JoinDialog";
import { useBoard } from "@/hooks/use-board";
import { COLUMNS, initials, type ColumnId, type Task } from "@/lib/kanban";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Team Kanban — Simple Shared Task Board" },
      {
        name: "description",
        content:
          "Team Kanban is a clean, drag-and-drop task board with To Do, In Progress and Done columns for small teams.",
      },
      { property: "og:title", content: "Team Kanban — Simple Shared Task Board" },
      {
        property: "og:description",
        content:
          "A minimal collaborative Kanban board: add tasks, set priorities and drag cards across three columns.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Board,
});

function Board() {
  const { tasksIn, user, ready, joinBoard, upsertTask, deleteTask, moveTask } = useBoard();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Task | null>(null);
  const [dragging, setDragging] = useState<Task | null>(null);

  const openNew = () => {
    setEditing(null);
    setDialogOpen(true);
  };

  const openEdit = (task: Task) => {
    setEditing(task);
    setDialogOpen(true);
  };

  const handleDrop = (status: ColumnId, index: number) => {
    if (dragging) moveTask(dragging.id, status, index);
    setDragging(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-4 sm:px-6">
          <div className="grid size-8 place-items-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
            K
          </div>
          <h1 className="text-base font-semibold tracking-tight text-foreground">Team Kanban</h1>

          <div className="ml-auto flex items-center gap-3">
            {user ? (
              <span className="hidden items-center gap-2 rounded-full border border-border py-1 pl-1 pr-3 text-xs font-medium text-muted-foreground sm:inline-flex">
                <span className="grid size-6 place-items-center rounded-full bg-secondary text-[10px] font-semibold text-secondary-foreground">
                  {initials(user)}
                </span>
                {user}
              </span>
            ) : null}
            <Button size="sm" onClick={openNew}>
              <Plus className="size-4" />
              Add Task
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
        <div className="grid gap-4 md:grid-cols-3">
          {COLUMNS.map((col) => (
            <BoardColumn
              key={col.id}
              id={col.id}
              title={col.title}
              hint={col.hint}
              tasks={tasksIn(col.id)}
              draggingId={dragging?.id ?? null}
              onEdit={openEdit}
              onDelete={setPendingDelete}
              onDragStart={setDragging}
              onDragEnd={() => setDragging(null)}
              onDrop={handleDrop}
            />
          ))}
        </div>
      </main>

      <TaskDialog
        open={dialogOpen}
        task={editing}
        onOpenChange={setDialogOpen}
        onSave={upsertTask}
      />

      <JoinDialog open={ready && !user} onJoin={joinBoard} />

      <AlertDialog
        open={pendingDelete !== null}
        onOpenChange={(open) => !open && setPendingDelete(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete this task?</AlertDialogTitle>
            <AlertDialogDescription>
              &ldquo;{pendingDelete?.title}&rdquo; will be removed from the board. This can&apos;t
              be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (pendingDelete) deleteTask(pendingDelete.id);
                setPendingDelete(null);
              }}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
