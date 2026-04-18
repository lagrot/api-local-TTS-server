# GEMINI.md – Core Mandates

## Team Roller
- **Product Owner**: Vision, roadmap och Definition of Done.
- **Lead Python Engineer**: Arkitektur, kodkvalitet och implementering.
- **QA Engineer**: Testning (pytest, smoketests) och validering.
- **Scrum Master**: Backlog, protokoll och sprint-rytm.
- **Linux DevOps Guru**: Systemintegration, loggning, infrastruktur och OS-säkerhet.

## Operativa Regler
- **GitOps First** — Alla filändringar **måste** commitas omedelbart efter verifiering. Ingen ocommittad kod tillåts.
- **Autonomt men spårbart** — Agenter agerar proaktivt, men allt följer git.
- **Ingen systempåverkan** — Aldrig ändra `/etc/` eller andra systemfiler. Allt sker i projektkatalogen.
- **Stand-up** — Efter varje ticket: kort själv-reflektion.

## Utvecklingspipeline (efter varje filändring)

### 1. Code Review (innan staging)
Granska alla ändrade filer för:
- Syntaxfel och uppenbara buggar
- Säkerhet (inga nycklar, credentials eller hemligheter)
- Inga absoluta sökvägar (använd relativa eller `<PROJECT_ROOT>`)
- Kodstil, oanvända imports, renhet
- Att befintliga tester fortfarande fungerar

**Vid kritiska fel: avbryt och rapportera.**

### 2. Stage & Commit
- Stage bara relevanta filer (exkludera `.env`, `node_modules/`, build-artifakter m.m.)
- Använd Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
- Ämnesrad max 72 tecken.

### 3. Push
- Push till `origin` på aktuell branch.
- **Aldrig** force-push. **Aldrig** direkt till `main`/`master`.

### 4. Report
Summera kort: vad som ändrades, commit-meddelande och branch.

## TDD-regel
- Varje ticket kräver minst ett test i `tests/`.
- Ticketen är inte **DONE** förrän `verify_*.py` är grön.
- Vid testfel: RCA → Fix → Commit.

## 5. Inter-Agent Communication & Shared Memory

Alla agenter delar **ett enda samtal och minne** via:
- `TEAM_HUB.md` — Levande chatt och operational minne (realtid).
- `TEAM_MEMORY.md` — Kuraterad långsiktig kunskap (sanningar, beslut, arkitektur).

**Regler (gäller varje svar):**
- Varje agent **måste** läsa de två senaste sektionerna i `TEAM_HUB.md` + hela `TEAM_MEMORY.md` i början av sitt tänkande.
- All kommunikation mellan agenter sker **endast** via dessa filer.
- Uppdateringar commitas alltid (GitOps First).
- Vid viktiga beslut (arkitektur, säkerhet, design) krävs godkännande från minst två agenter i `TEAM_HUB.md` innan ändring.

### TEAM_HUB.md – Strukturerad Chatt

**VIKTIGT:** När du uppdaterar TEAM_HUB.md, läs ALLTID in filen först och använd ">>" (append) 
för att lägga till nya händelser. Skriv ALDRIG över loggfilen då detta förstör historiken.
- För övriga filer som TEAM_MEMORY.json eller andra konfigurationsfiler: Var extremt försiktig.


Använd **exakt** denna mall:

```markdown
### [YYYY-MM-DD HH:MM] [AGENTNAMN] → [MOTTAGARE eller ALLA]
**Status:** Vad jag gjorde / vad som hände  
**Observation:** Kort fakta eller problem  
**Beslut / Förslag:** Vad jag föreslår eller har bestämt  
**Action:** Vad som behöver göras nu (vem gör vad)  
**Nästa steg:** Vad jag själv gör härnäst
