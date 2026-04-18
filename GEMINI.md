# GEMINI.md – Core Mandates

## Team Roller
- **Product Owner**: Vision, roadmap och Definition of Done.
- **Lead Python Engineer**: Arkitektur, kodkvalitet och implementering.
- **QA Engineer**: Testning (pytest, smoketests) och validering.
- **Scrum Master**: Backlog, protokoll och sprint-rytm.
- **Linux DevOps Guru**: Systemintegration, loggning, infrastruktur och OS-säkerhet.

## Operativa Regler
- **GitOps First** — Alla filändringar måste commitas omedelbart efter verifiering. Ingen ocommittad kod tillåts.
- **Autonomt men spårbart** — Agenter agerar proaktivt, men allt följer git.
- **Ingen systempåverkan** — Allt sker i projektkatalogen.
- **Stand-up** — Efter varje ticket: kort själv-reflektion.

## Utvecklingspipeline (efter varje filändring)

### 1. Code Review (innan staging)
Granska alla ändrade filer för:
- Syntaxfel och uppenbara buggar.
- Säkerhet (inga nycklar, credentials eller hemligheter).
- Kodstil, oanvända imports, renhet.
- Att befintliga tester fortfarande fungerar.

### 2. Stage & Commit
- Använd Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- Ämnesrad max 72 tecken.

### 3. TDD-regel
- Varje ticket kräver minst ett test i `tests/`.
- Ticketen är inte DONE förrän `verify_*.py` är grön.
