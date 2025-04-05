# AI Assistant Modes for IsopGem

This directory contains specialized assistant modes that tailor the AI's behavior for different tasks. Each mode optimizes the assistant's responses for a specific type of development activity.

## Available Modes

| Mode | Purpose | Activation Command |
|------|---------|-------------------|
| PLAN/Architect | System design and architecture planning | `/mode plan` |
| CODE/Implementation | Writing new code and implementing features | `/mode code` |
| DEBUG | Troubleshooting and fixing issues | `/mode debug` |
| REFACTOR | Improving code quality without changing functionality | `/mode refactor` |
| REVIEW | Evaluating code quality and providing feedback | `/mode review` |
| TEST | Creating test plans and test implementations | `/mode test` |
| DOCUMENT | Creating or improving documentation | `/mode document` |
| OPTIMIZE | Improving performance and efficiency | `/mode optimize` |
| UX | Enhancing user interfaces and user experience | `/mode ux` |
| LEARN | Exploring and understanding unfamiliar code or concepts | `/mode learn` |
| DEVOPS | Handling deployment, infrastructure, and operations | `/mode devops` |
| MODULARIZE | Breaking down monolithic code into reusable modules | `/mode modularize` |
| BRAINSTORM | Generating ideas and exploring concepts without code | `/mode brainstorm` |

## Core Rules

In addition to modes, the system includes core rules that apply across all interactions:

| Rule | Purpose | Application |
|------|---------|-------------|
| Project Architecture | Enforces the 5-pillar structure for code organization | When creating or refactoring components |
| File Documentation | Ensures all new files are properly documented | Automatically applied to any new file creation |
| File Tracker | Maintains a centralized file tracker document | Updates when files are added or modified |

## How to Use Modes

There are two ways to activate a mode:

1. **Command-based activation**: Type the activation command in your message
   ```
   /mode debug
   ```

2. **Natural language activation**: Simply ask for the mode in your message
   ```
   Can you switch to DEBUG mode to help me fix this error?
   ```

Once a mode is activated, the assistant will follow the specialized rules and response format for that mode until you change to a different mode or reset.

## Example Mode Usage

**PLAN mode example:**
```
/mode plan

I need to design a new feature for storing and retrieving user preferences in our application.
```

**DEBUG mode example:**
```
/mode debug

I'm getting this error when I run the application:
Error: Cannot read property 'value' of undefined at processInput (/src/utils.js:42)
```

**CODE mode example:**
```
/mode code

Please implement a function that validates email addresses according to RFC 5322.
```

**UX mode example:**
```
/mode ux

Can you help improve this navigation menu to be more user-friendly?
```

**LEARN mode example:**
```
/mode learn

How does the Python context manager protocol work? I'm confused about __enter__ and __exit__.
```

**BRAINSTORM mode example:**
```
/mode brainstorm

We need to come up with ideas for a feature that helps users visualize their data over time.
```

## Creating New Modes

To create a new mode:

1. Create a new `.mdc` file in this directory
2. Follow the standard mode template structure:
   - YAML frontmatter with description
   - Critical rules section
   - Response structure section
   - Examples section with valid and invalid examples
3. Update this README to include the new mode

## Mode Template Structure

Each mode file follows this structure:

```markdown
---
description: `Brief description of the mode's purpose`
globs: 
alwaysApply: false
---

# MODE_NAME Mode

## Critical Rules

- Rule 1
- Rule 2
- ...

## Response Structure

1. **Section 1**: Description
2. **Section 2**: Description
3. ...

## Examples

<example>
User: Example user query

Response:

Example assistant response showing proper format
</example>

<example type="invalid">
User: Example user query

Response:

Example of improper response format
</example>
``` 