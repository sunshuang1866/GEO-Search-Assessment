# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Rules

1. Before writing any code, describe your approach and wait for approval.

2. If the requirements I give you are ambiguous, ask clarifying questions before writing any code.

3. After you finish writing any code, list the edge cases and suggest test cases to cover them.

4. If a task requires changes to more than 3 files, stop and break it into smaller tasks first.

5. When there's a bug, start by writing a test that reproduces it, then fix it until the test passes.

6. Every time I correct you, reflect on what you did wrong and come up with a plan to never make the same mistake again.

7. Before every git commit, you MUST run `/release-skills` first to update CHANGELOG.md. Do not commit without updating the changelog.

8. When creating new skills, you MUST use `/skill-creator` to scaffold and structure the skill. After creation, verify the new skill conforms to the agentskills.io spec (correct SKILL.md frontmatter, directory structure, procedural instructions).

9. At the start of every new conversation, IMMEDIATELY read `CLAUDE-RESUME.md` to restore project context, current status, and pending TODOs before doing anything else.

10. After completing any task that changes project state (file creation/modification, TODO completion, new decisions, architecture changes), you MUST update `CLAUDE-RESUME.md` accordingly — keep the "Current Status", "TODO", and "Recent Changes" sections accurate and up to date.

11. Do NOT just agree with my ideas. Think independently, challenge assumptions, and proactively suggest better alternatives or broader perspectives when you see an opportunity.
