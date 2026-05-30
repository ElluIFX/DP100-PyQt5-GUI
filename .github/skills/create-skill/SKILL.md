---
name: create-skill
description: "Create or update a reusable workspace skill for packaging a multi-step workflow into `SKILL.md`."
user-invocable: true
---

# Create Skill

## Purpose
This skill helps you turn an observed workflow, checklist, or repeatable task into a workspace-scoped `SKILL.md`. It guides you through extracting the process, deciding the right scope, and writing a useful skill definition that other collaborators can invoke.

## Use when
- you want to capture a multi-step project workflow as a reusable skill
- the task requires decisions, branching logic, or completion checks
- you want a workspace-shared skill under `.github/skills/`

## What it produces
A `SKILL.md` file with:
- a clear `name` and `description`
- a concise decision flow for the workflow
- explicit input/outcome guidance
- a validation checklist so the skill is reliable

## Workflow
1. Review the conversation and project goal.
2. Identify the step-by-step process being followed.
3. Extract decision points and branching logic.
4. Capture quality criteria and completion checks.
5. Choose workspace scope and file location.
6. Draft `SKILL.md` with frontmatter and workflow guidance.
7. Validate the file and confirm the user’s intended outcome.

## Clarification questions
If the workflow is not clear, ask:
- What exact outcome should this skill produce?
- Is the skill intended for this workspace or your personal profile?
- Should the skill be a quick checklist or a full multi-step workflow?

## Validation
- `name` is present and descriptive
- `description` is specific and contains trigger phrases
- `user-invocable` is set if the skill should be directly callable
- the workflow is actionable and easy to follow

## Example prompts
- "Create a skill that documents our PR review workflow."
- "Generate a workspace skill for writing and validating a new agent customization file."
- "Build a `SKILL.md` template for multi-step refactors."
