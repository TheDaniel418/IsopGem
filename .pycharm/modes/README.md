# AI Assistant Modes for PyCharm

This directory contains specialized assistant modes that tailor the AI's behavior for different tasks in PyCharm. Each mode optimizes the assistant's responses for a specific type of development activity.

## Available Modes

| Mode | Purpose | Activation Command |
|------|---------|-------------------|
| PLAN/Architect | System design and architecture planning | `[PLAN]` |
| CODE/Implementation | Writing new code and implementing features | `[CODE]` |
| DEBUG | Troubleshooting and fixing issues | `[DEBUG]` |
| REFACTOR | Improving code quality without changing functionality | `[REFACTOR]` |
| REVIEW | Evaluating code quality and providing feedback | `[REVIEW]` |
| TEST | Creating test plans and test implementations | `[TEST]` |
| DOCUMENT | Creating or improving documentation | `[DOCUMENT]` |
| OPTIMIZE | Improving performance and efficiency | `[OPTIMIZE]` |
| UX | Enhancing user interfaces and user experience | `[UX]` |
| LEARN | Exploring and understanding unfamiliar code or concepts | `[LEARN]` |
| DEVOPS | Handling deployment, infrastructure, and operations | `[DEVOPS]` |
| MODULARIZE | Breaking down monolithic code into reusable modules | `[MODULARIZE]` |
| BRAINSTORM | Generating ideas and exploring concepts without code | `[BRAINSTORM]` |

## Core Rules

In addition to modes, the system includes core rules that apply across all interactions:

| Rule | Purpose | Application |
|------|---------|-------------|
| Project Architecture | Enforces the 5-pillar structure for code organization | When creating or refactoring components |
| File Documentation | Ensures all new files are properly documented | Automatically applied to any new file creation |
| File Tracker | Maintains a centralized file tracker document | Updates when files are added or modified |

## How to Use Modes in PyCharm

To activate a mode in PyCharm, simply start your message to the AI Assistant with the mode indicator in square brackets:
