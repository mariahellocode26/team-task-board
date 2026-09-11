import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function JoinDialog({ open, onJoin }: { open: boolean; onJoin: (name: string) => void }) {
  const [name, setName] = useState("");

  return (
    <Dialog open={open}>
      <DialogContent showCloseButton={false} className="sm:max-w-md">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (name.trim()) onJoin(name.trim());
          }}
        >
          <DialogHeader>
            <DialogTitle>Welcome to Team Kanban</DialogTitle>
            <DialogDescription>Enter your display name to join the board.</DialogDescription>
          </DialogHeader>
          <div className="mt-5 space-y-2">
            <Label htmlFor="display-name">Display name</Label>
            <Input
              id="display-name"
              autoFocus
              placeholder="e.g. Maria"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <Button type="submit" className="mt-6 w-full" disabled={!name.trim()}>
            Join Board
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
