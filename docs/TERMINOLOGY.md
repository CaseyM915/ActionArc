# ActionArc Terminology

## ActionArc

The application.

---

## Arc

A complete automation workflow.

An Arc connects Triggers to Actions while managing schedules, variables, logging, retry behavior, and conditions.

---

## Trigger

A component responsible for detecting when an event has occurred.

Examples:

- Folder Changed
- New Active Directory User
- New GitHub Release
- Linear Issue Created

---

## Action

A component responsible for performing work.

Examples:

- Run PowerShell
- Send Slack Message
- Create GitHub Issue
- Move File

---

## Provider

A package containing related Triggers and Actions.

Examples:

Filesystem Provider

GitHub Provider

Slack Provider

Active Directory Provider

Linear Provider

---

## Variable

Information produced by a Trigger or Action that can be consumed later in an Arc.

Examples:

FileName

UserName

Version

Repository

---

## Condition

Optional logic determining whether an Arc should continue executing.

---

## Arc Run

One execution instance of an Arc.

Contains:

- Start Time
- End Time
- Status
- Logs
- Outputs

---

## Engine

The core execution system.

Responsible for:

- Trigger evaluation
- Action execution
- Scheduling
- Logging

---

## CLI

Command-line interface.

Provides access to Engine functionality for scripting and diagnostics.

---

## Service

Windows background service responsible for executing scheduled Arcs.

Runs independently of user logins.

---

## Dashboard

The primary interface of ActionArc.

Displays Arc health, status, history, and management controls.

---

## Library

A collection of reusable Triggers, Actions, Providers, or Arc templates.

---

## ArcPack (Tentative)

A portable package used to distribute reusable automation content.

May contain:

- Providers
- Triggers
- Actions
- Arc Templates
- Documentation