# ActionArc Product Specification

## Vision

ActionArc is a local-first automation platform that allows users to build reusable automation workflows ("Arcs") from Triggers and Actions.

Whether using built-in integrations or custom scripts, ActionArc is designed to grow with the user—from simple no-code automations to highly customized enterprise workflows.

---

## Goals

- Make automation approachable.
- Never limit advanced users.
- Keep all automations understandable.
- Keep the platform local-first.
- Allow automation to scale from one simple task to an entire environment.

---

## Core Concepts

An Arc consists of:

- Trigger(s)
- Conditions
- Variables
- Action(s)
- Schedule
- Logging
- Retry behavior

An Arc represents one complete automation workflow.

---

## Roadmap

| Version          | Working Name         | Scope                                                                                                                                      | Exit Condition                                                                                                                                                         |
|------------------|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **0.1.0**        | Engine Foundation    | Core models, registry, runner, scheduler, controller, JSON loading, and proof-of-concept execution                                         | An example Arc can load and run through the complete engine pipeline.                                                                                                  |
| **0.2.0**        | Dashboard Demo       | First PySide6 dashboard connected to `EngineController`, with engine state, loaded Arcs, and Run Now                                       | The user can visibly control and observe the engine without using the CLI.                                                                                             |
| **0.3.0**        | Arc Management       | Multiple Arcs load from storage; create, duplicate, enable, disable, and delete are supported                                              | The application is no longer centered around a single hardcoded example Arc.                                                                                           |
| **0.4.0**        | Basic Arc Editor     | Users can edit Arc identity, schedule, trigger, and actions through the GUI                                                                | A basic Arc can be created and saved without manually editing JSON.                                                                                                    |
| **0.5.0**        | Useful Automation    | A focused starter set of practical local triggers and actions                                                                              | Someone can use ActionArc for real local automation rather than only demonstrations.                                                                                   |
| **0.6.0**        | Observable Runs      | Persistent run history, clear success/failure states, errors, timestamps, and action-level results                                         | Users can understand what ran and diagnose common failures from the GUI.                                                                                               |
| **0.7.0**        | Arc Logic            | Variables, trigger outputs, action inputs, basic conditions, and failure behavior                                                          | Data can move through an Arc and execution can make simple decisions.                                                                                                  |
| **0.8.0**        | Background Engine    | Engine operation is separated enough from the GUI to run reliably in the background, with startup and reconnection behavior                | Arcs continue to operate without the dashboard remaining open.                                                                                                         |
| **0.9.0**        | Feature Complete     | The entire intended v1 feature set exists                                                                                                  | No major v1 feature remains unimplemented.                                                                                                                             |
| **0.9.1–0.9.14** | Stabilization Builds | Packaging, installer, settings, import/export, validation, migrations, first-run experience, documentation, testing, and accumulated fixes | Internal testing finds no known release-blocking architectural or data-safety problem.                                                                                 |
| **0.9.15**       | The 915 Build        | Exact intended v1 candidate distributed to a small tester group                                                                            | Testers can install, create Arcs, run them over time, update or reinstall safely, and report no unresolved release-blocking bugs. For context, 915 is my lucky number. |
| **1.0.0**        | First Public Release | Publicly supported first version of ActionArc                                                                                              | `0.9.15` passes testing, only approved fixes are applied, and release materials are complete.                                                                          |

### Future

- Built-in integrations
- Provider SDK
- Community Arc sharing
- Arc marketplace
- Cloud sync
- Remote management
- AI-assisted Arc creation

## Product Philosophy

ActionArc should never force users to outgrow it.
Beginners should be able to automate using built-in integrations.
ActionArc should make the simple things simple without making advanced automation difficult.
Experts should be able to extend every part of the platform.