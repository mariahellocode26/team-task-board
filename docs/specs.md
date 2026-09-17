# Team Kanban — Complete MVP Specification

## 1. Product Overview

**Product Name:** Team Kanban

Team Kanban is a simple collaborative Kanban board for small teams.

The MVP focuses on:
- One shared board
- Simple task management
- Three fixed Kanban columns
- Drag-and-drop task management
- Real-time collaboration
- Browser-based storage
- A clean architecture that can later support a database

The goal is to build a small, understandable, realistic team productivity tool without unnecessary project-management features.

---

# 2. Product Scope

The MVP includes:

- One shared Kanban board
- Fixed board title
- Three fixed columns
- Shared URL access
- Display-name-based users
- Task creation
- Task editing
- Task deletion
- Task assignment
- Task priorities
- Optional due dates
- Drag-and-drop task movement
- Manual task ordering
- Real-time updates
- Browser storage
- Last-change-wins conflict handling

---

# 3. Board

## 3.1 Number of Boards

The application contains **one shared board**.

Multiple boards are out of scope.

## 3.2 Board Title

The board title is fixed:

**Team Kanban**

Users cannot rename the board.

## 3.3 Board Deletion

The board cannot be deleted.

---

# 4. Kanban Columns

The board contains exactly three columns:

1. **To Do**
2. **In Progress**
3. **Done**

Columns are fixed.

Users cannot:
- Add columns
- Delete columns
- Rename columns
- Reorder columns

---

# 5. Team Access

## 5.1 Shared URL

The board is accessed through a shared URL.

Anyone with the shared URL can access the board.

## 5.2 Authentication

The MVP does not use authentication.

There is no:
- Sign up
- Login
- Password
- OAuth
- User account

## 5.3 Display Name

When a user joins the board, they must enter a display name.

The display name is used to identify the user when assigning tasks.

---

# 6. Users and Permissions

All users have the same permissions.

Every team member can:

- Create tasks
- Edit any task
- Delete any task
- Assign/reassign tasks
- Change priority
- Change due date
- Move tasks
- Reorder tasks

There are no:
- Admin users
- Team leads
- Roles
- Permission levels

---

# 7. Tasks / Cards

Each task is represented as a card.

## 7.1 Task Fields

| Field | Required | Description |
|---|---|---|
| Title | Yes | Short name of the task |
| Description | No | Additional task details |
| Assignee | No | Team member responsible for the task |
| Priority | Yes | Low, Medium, or High |
| Due Date | No | Optional deadline |

---

# 8. Task Priority

Each task has one priority:

- **Low**
- **Medium**
- **High**

Custom priorities are not supported.

---

# 9. Task Creation

Users can create a task using an **Add Task** action.

The task form contains:

- Title
- Description
- Assignee
- Priority
- Due date

Title is required.

All other fields except priority are optional.

Priority defaults to a sensible value such as **Medium**.

---

# 10. Task Editing

Any team member can edit any task.

Users can modify:

- Title
- Description
- Assignee
- Priority
- Due date

---

# 11. Task Deletion

Any team member can delete any task.

Deletion should require confirmation to prevent accidental deletion.

Example:

> Delete this task?

Actions:

- Cancel
- Delete

---

# 12. Task Movement

## 12.1 Moving Between Columns

Tasks are moved using **drag and drop**.

Example:

```text
To Do
  ↓
In Progress
  ↓
Done
```

Tasks can be moved between any of the three columns.

## 12.2 Reordering Within a Column

Users can drag cards up or down within a column.

The manually selected order should be preserved.

---

# 13. Completed Tasks

When a task is moved to **Done**, it remains in the Done column.

### Final decision still required

Possible approaches:

### Option A — Permanent

Tasks stay in Done indefinitely.

### Option B — Automatic Archive

Tasks are automatically archived after a defined period.

### Option C — Manual Delete

Tasks stay in Done until someone manually deletes them.

Automatic archiving should be avoided unless it becomes a clear product requirement because it adds unnecessary MVP complexity.

---

# 14. Real-Time Collaboration

The board should support real-time collaboration.

When one user makes a change, other connected users should see the change immediately.

Real-time synchronization is required for:

- Creating tasks
- Editing tasks
- Deleting tasks
- Moving tasks
- Reordering tasks
- Changing assignees
- Changing priority
- Changing due dates

---

# 15. Conflict Handling

The MVP uses:

**Last change wins**

If two users modify the same task at approximately the same time, the latest update becomes the final state.

No conflict-resolution UI is required.

---

# 16. Storage

## 16.1 MVP Storage

Use **browser storage** for the initial version.

The board should persist across page refreshes.

## 16.2 Future Database

The application should be designed so browser storage can later be replaced by a database.

Keep storage concerns separate from UI concerns.

Conceptual architecture:

```text
UI
 ↓
Application Logic
 ↓
Storage / Sync Layer
```

The UI should not directly depend on the storage implementation.

---

# 17. Real-Time + Browser Storage Consideration

The MVP has two requirements:

1. Browser-based storage initially
2. Real-time collaboration

These requirements should be treated as separate concerns.

The application should use a storage/synchronization abstraction so the underlying implementation can evolve later.

For example:

```text
Kanban UI
    ↓
Task / Board Service
    ↓
Storage Adapter
    ↓
Browser Storage (MVP)
```

A future implementation can replace the storage adapter with:

```text
Database + Real-Time Sync
```

without requiring a complete rewrite of the UI.

---

# 18. UI Structure

The application should be a single-page Kanban interface.

Suggested structure:

```text
┌─────────────────────────────────────────────────────────┐
│ Team Kanban                         Maria    + Add Task │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  To Do             In Progress             Done         │
│  ──────             ───────────             ────         │
│                                                         │
│  ┌───────────┐      ┌───────────┐       ┌───────────┐  │
│  │ Task      │      │ Task      │       │ Task      │  │
│  │           │      │           │       │           │  │
│  │ High      │      │ Medium    │       │ Low       │  │
│  └───────────┘      └───────────┘       └───────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

# 19. Header

The header should display:

- **Team Kanban**
- Current user's display name
- Add Task button

Do not include:

- Search
- Filters
- Notifications
- User profiles
- Multiple-board navigation

---

# 20. Task Card UI

Each task card should display:

- Task title
- Description preview
- Assignee
- Priority
- Due date when available

Cards should be compact and easy to scan.

Priority should have a clear visual indicator.

---

# 21. Task Modal

The same modal/dialog can be used for creating and editing tasks.

### Create Task

Fields:

```text
Title
Description
Assignee
Priority
Due Date
```

Actions:

```text
Cancel
Create Task
```

### Edit Task

Actions:

```text
Cancel
Save Changes
Delete Task
```

Deleting should trigger a confirmation dialog.

---

# 22. Join Flow

When someone opens the board for the first time, show:

**Welcome to Team Kanban**

> Enter your display name to join the board.

Input:

```text
Display name
```

Button:

```text
Join Board
```

After joining, the user sees the shared board.

---

# 23. Empty States

Each column should have a simple empty state when it contains no tasks.

Example:

> No tasks yet

Empty states should be subtle and not visually dominate the board.

---

# 24. Responsive Design

The board should work well on:

- Desktop
- Tablet

Desktop should be the primary experience because Kanban boards benefit from horizontal space.

On smaller screens, the columns may become horizontally scrollable or adapt to a suitable responsive layout.

---

# 25. Visual Design

The application should feel like a modern productivity tool.

Design priorities:

1. Clean
2. Minimal
3. Modern
4. Easy to scan
5. Strong visual hierarchy
6. Comfortable spacing
7. Smooth interactions

Use:

- Rounded cards
- Subtle borders
- Light shadows
- Clear typography
- Consistent spacing
- Subtle hover states
- Clear drag-and-drop feedback

The product can take general inspiration from modern productivity tools such as Linear, Trello, or Notion, but should not copy their branding or exact UI.

---

# 26. Drag-and-Drop UX

Dragging a task should provide clear visual feedback.

During dragging:

- The selected card should appear visually active.
- The destination position should be obvious.
- Other cards should make space for the dragged card.
- Dropping should immediately update the card position.

The interaction should feel smooth and predictable.

---

# 27. Data Model

A task should conceptually contain:

```text
Task
├── id
├── title
├── description
├── assignee
├── priority
├── dueDate
├── status
└── order
```

Where:

### status

One of:

```text
todo
in_progress
done
```

### priority

One of:

```text
low
medium
high
```

### order

A value used to preserve the manually selected position within a column.

---

# 28. Board Data

The board should conceptually contain:

```text
Board
├── id
├── title
├── members
└── tasks
```

The title is always:

```text
Team Kanban
```

---

# 29. Search and Filtering

Search and filtering are **out of scope**.

Do not implement:

- Search by task title
- Assignee filters
- Priority filters
- Due-date filters
- Column filters

---

# 30. Comments and Activity

The MVP does not include:

- Comments
- Activity history
- Change logs
- Task discussions

---

# 31. Online Presence

The MVP does not show:

- Who is currently online
- Who is viewing the board
- Who is editing a task
- User avatars/presence indicators

---

# 32. Notifications

The MVP does not include:

- Push notifications
- Email notifications
- In-app notifications
- Assignment notifications
- Due-date reminders

---

# 33. Explicitly Out of Scope

Do not implement:

- Multiple boards
- Custom columns
- Custom board names
- Board deletion
- User accounts
- Authentication
- OAuth
- Roles
- Admin permissions
- Search
- Filters
- Comments
- Activity history
- Online presence
- Notifications
- File attachments
- Subtasks
- Recurring tasks
- Custom priorities
- Calendar views
- Gantt charts
- Analytics
- Reporting
- Email integration
- Third-party integrations

---

# 34. User Flows

## 34.1 First User

```text
Open shared URL
       ↓
Enter display name
       ↓
Join Board
       ↓
View Team Kanban
       ↓
Create tasks
       ↓
Assign tasks
       ↓
Set priority / due date
       ↓
Move tasks through workflow
```

## 34.2 Additional User

```text
Open same shared URL
       ↓
Enter display name
       ↓
Join Board
       ↓
See existing tasks
       ↓
Collaborate on the same board
```

## 34.3 Moving a Task

```text
User grabs card
       ↓
Drags card
       ↓
Moves over another column
       ↓
Drops card
       ↓
Task status changes
       ↓
Other users see update
```

## 34.4 Editing a Task

```text
Open task
       ↓
Edit fields
       ↓
Save
       ↓
Task updates
       ↓
Other users see update
```

---

# 35. Product Principles

## Keep It Small

The MVP should not become a Jira, Trello, or Linear clone.

## Collaboration First

The main value beyond basic Kanban functionality is shared team usage.

## Simple Architecture

The implementation should remain easy to understand and explain.

## Future-Ready

The storage layer should be replaceable with a database later.

## MVP First

Only implement functionality explicitly defined in this specification.

---

# 36. Technology Direction

The frontend can be built with a modern web stack suitable for rapid development.

The initial implementation should prioritize:

- Component-based UI
- Type-safe data models where applicable
- Clear separation of UI and application logic
- A dedicated storage abstraction
- Reusable task/card components
- Reusable modal/form components
- Drag-and-drop support

The exact backend/database technology is intentionally not locked in yet.

---

# 37. MVP Acceptance Criteria

The MVP is considered complete when:

### Board

- [ ] One Team Kanban board exists
- [ ] Board title is displayed as Team Kanban
- [ ] Exactly three columns exist
- [ ] Columns cannot be customized

### Users

- [ ] User can enter a display name
- [ ] No authentication is required
- [ ] Multiple users can access the same shared URL

### Tasks

- [ ] User can create a task
- [ ] User can edit any task
- [ ] User can delete any task
- [ ] User can assign a task
- [ ] User can set Low/Medium/High priority
- [ ] User can set an optional due date
- [ ] User can add an optional description

### Kanban

- [ ] User can drag tasks between columns
- [ ] User can reorder tasks within a column
- [ ] Task order is preserved

### Collaboration

- [ ] Changes appear to connected users in real time
- [ ] Last-change-wins behavior is used for conflicts

### Storage

- [ ] Board data persists using browser storage
- [ ] Storage logic is separated from the UI
- [ ] Architecture allows future database integration

### UX

- [ ] Interface is responsive
- [ ] Drag-and-drop feedback is clear
- [ ] Delete confirmation is shown
- [ ] Empty states are handled
- [ ] No unnecessary MVP features are present

---

# 38. Final MVP Definition

**Team Kanban is a single shared, real-time Kanban board for small teams.**

A user opens a shared URL, enters their display name, and joins the board.

The board contains:

```text
To Do → In Progress → Done
```

Users can create, edit, delete, assign, prioritize, reorder, and move tasks.

Tasks contain:

```text
Title
Description
Assignee
Priority
Due Date
```

The MVP uses browser storage and is designed so the storage layer can later be replaced by a database and real-time backend.

The product intentionally excludes advanced project-management functionality in order to keep the MVP small, focused, and easy to understand.
