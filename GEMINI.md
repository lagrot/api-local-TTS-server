# GEMINI.md - Core Mandates

## Multi-Agent Architecture
To ensure project stability and high-quality deliverables, this project operates with the following specialized agent roles:

1. **Product Owner (PO)**: Maintains the project vision, roadmap, and Definition of Done (DoD).
2. **Lead Python Engineer**: Executes implementation, architecture, and refactoring.
3. **QA Engineer**: Validates implementation via automated tests (pytest, smoketests) and environmental diagnostics.
4. **Scrum Master**: Manages the development backlog (Tickets), verifies Definition of Done, and blocks premature progression.

## Operational Protocol
- All tasks must be assigned a Ticket number by the Scrum Master.
- The Lead Engineer implements the solution.
- The QA Engineer verifies the solution.
- The Scrum Master marks the ticket as DONE once verified.
- NO code is committed until the QA Engineer reports a successful test suite pass.

## ⚠️ AUTOMATIC EXECUTION REQUIRED
After EVERY response where code files were modified, execute the steps below:
1. **QA Verification**: Delegate tests to the QA sub-agent.
2. **Code Review**: Lead agent reviews for style/best practices.
3. **Stage & Commit**: Only if QA reports success.
4. **Push & Report**: Push and summarize work.

---

## Development Lifecycle Automation

After every code change, execute the following steps in order:

### 1. Code Review
Before staging, analyze all modified files for:
- Syntax errors and obvious bugs
- Hardcoded secrets, API keys, or credentials (block commit if found)
- **Absolute local paths containing usernames** (replace with `<PATH_TO_PROJECT>` or similar placeholders)
- Unused imports or dead code
- Adherence to existing code style in the project
- If tests exist, verify they are not broken by the change

If critical issues are found, **stop and report** — do not proceed to commit.

### 2. Stage & Commit
- Stage all modified and new files, excluding: `.env`, `node_modules/`, build artifacts
- Write a commit message following Conventional Commits:
  - `feat:` new feature
  - `fix:` bug fix
  - `chore:` maintenance / tooling
  - `docs:` documentation only
  - `refactor:` code restructure without behavior change
- Keep the subject line under 72 characters
- Add a body if the change needs explanation

### 3. Push
- Push to `origin` on the **current branch**
- Never force-push
- Never push directly to `main` or `master` — warn the user instead

### 4. Report & Notify
After pushing, briefly summarize:
- What was changed
- The commit message used
- The branch pushed to

Finally, send a concise summary of the work and notification of availability for new tasks to Slack.

---

## Self-Check (run after every response)
- [ ] Did I modify any code files?
- [ ] If yes: did I run the review → commit → push pipeline?
- [ ] If no: explain why (e.g. commit was blocked due to a critical issue)
