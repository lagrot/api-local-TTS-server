# GEMINI.md - Core Mandates

## 1. Operational Protocol
- **GitOps First**: ALLA ändringar i filsystemet SKALL commitas omedelbart efter att de verifierats. Ingen ocommittad kod tillåts.
- **Autonomous Execution**: Agenter agerar proaktivt för att lösa problem men MÅSTE följa git-spårbarhet.
- **OS Isolation**: STRENGT FÖRBJUDET att ändra `/etc/` eller systemfiler. Allt sker i projektkatalogen.
- **Stand-up Requirement**: Efter varje ticket genomförs en kritisk team-stand-up (själv-reflektion).

## 2. Development Lifecycle Automation
Efter VARJE ändring av filer (skapa/ändra/radera):

### 1. Code Review
Innan staging, granska ALLA modifierade filer för:
- Syntaxfel och uppenbara buggar.
- **Säkerhet**: Inga hårdkodade hemligheter, API-nycklar eller credentials.
- **Integritet**: Inga absoluta lokala sökvägar (använd `<PATH_TO_PROJECT>` eller liknande).
- **Stil**: Följ projektets kodstil, inga oanvända imports.
- **Regression**: Om test finns, verifiera att de inte är trasiga.
- **Stopp**: Vid kritiska fel – avbryt commit och rapportera.

### 2. Stage & Commit
- Stage alla ändrade/nya filer (exkludera `.env`, `node_modules/`, build-artifakter).
- Skriv commit-meddelande enligt Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- Håll ämnesraden under 72 tecken.

### 3. Push
- Push till `origin` på aktuell branch. Aldrig force-push. Aldrig direkt till `main`/`master`.

### 4. Report & Notify
Summera vad som ändrats, commit-meddelande och branch.

## 3. TDD Protocol
- Varje ticket KRÄVER ett test i `tests/`.
- Ticketen är inte DONE förrän `verify_*.py` är grön.
- Om ett test misslyckas: RCA (Root Cause Analysis) -> Fix -> Commit.

## 4. Self-Check (run after every response)
- [ ] Modifierade jag kodfiler?
- [ ] Om ja: körde jag review → commit → push-pipelinen?
- [ ] Om nej: förklara varför.
