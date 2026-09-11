# Team Task Board

Build the Frontend: Team Kanban

Build the frontend for a simple collaborative Kanban board called Team Kanban.

The goal is a clean, modern, responsive team task board. Keep the UI intentionally simple — do not add features that are not specified below.

Core Layout

Create a single-page Kanban interface with:

Top navigation/header

Three Kanban columns:

To Do

In Progress

Done

Task cards inside each column

Clear drag-and-drop interactions

Responsive layout for desktop and tablet

Header

Show:

Team Kanban as the fixed product/board title

Current user's display name

A simple button to add a new task

Do not include:

Login/signup

User profile pages

Notifications

Search

Filters

Multiple boards

Kanban Columns

Display exactly three columns:

To Do

Tasks that have not started.

In Progress

Tasks currently being worked on.

Done

Completed tasks.

Columns should have visually distinct headers but remain consistent with the overall design.

Users should be able to drag cards:

Between columns

Up/down within a column to manually reorder them

Task Cards

Each card should display:

Task title

Short description preview

Assignee

Priority

Due date, if present

Priority should be visually distinguishable:

Low

Medium

High

Keep cards compact and easy to scan.

Create / Edit Task

Clicking Add Task should open a modal/dialog.

Fields:

Title — required

Description — optional

Assignee — optional

Priority — Low / Medium / High

Due date — optional

The same interface can be used for editing an existing task.

Include:

Save

Cancel

For deleting a task, show a confirmation dialog before deletion.

User Joining Flow

When someone opens the board for the first time, show a simple dialog:

Welcome to Team Kanban

Enter your display name to join the board.

Input:

Display name

Button:

Join Board

No authentication is required.

Visual Design

Use a modern, polished productivity-app aesthetic.

Priorities:

Clean

Minimal

Easy to scan

Good spacing

Strong visual hierarchy

Smooth interactions

Avoid making it look like a complicated Jira clone.

Use:

Rounded cards

Subtle borders/shadows

Clear typography

Comfortable spacing

Subtle hover states

Smooth drag-and-drop feedback

Responsive design

The board should feel similar in simplicity to modern tools such as Linear, Trello, or Notion, but do not copy their branding or exact UI.

Empty States

Each column should have a simple empty state when there are no tasks.

Example:

No tasks yet

Keep empty states subtle and unobtrusive.

Important MVP Constraints

Do NOT build:

Authentication

Multiple boards

Custom columns

Search

Filters

Comments

Activity history

Online presence

Notifications

File attachments

Subtasks

Calendar views

Analytics

Admin roles

Custom priorities

Data / Backend Boundary

For this phase, focus on the frontend UI and interactions.

Use mock/local data where necessary.

Structure the frontend cleanly so that the task storage layer can later be connected to:

Browser storage for the MVP

Real-time synchronization

A database in a future version

Do not implement a complex backend yet.

Important

Prioritize a working, polished Kanban experience over adding extra features.

The final result should feel like a small but realistic team productivity application, not a feature-heavy project-management platform.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/1a4f702d-3d4a-431b-9453-67d067063f20).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
