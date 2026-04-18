# GEMINI.md - Core Mandates

## 1. Operational Protocol
- **GitOps First**: ALLA ändringar i filsystemet SKALL commitas omedelbart efter att de verifierats. Ingen ocommittad kod tillåts.
- **Autonomous Execution**: Agenter agerar proaktivt för att lösa problem men MÅSTE följa git-spårbarhet.
- **OS Isolation**: STRENGT FÖRBJUDET att ändra `/etc/` eller systemfiler. Allt sker i projektkatalogen.
- **Stand-up Requirement**: Efter varje ticket genomförs en kritisk team-stand-up (själv-reflektion).

## 2. Development Lifecycle Automation
Efter VARJE ändring av filer (skapa/ändra/radera):

1. **Review**: Granska för syntax, hemligheter, hårda sökvägar, stil.
2. **Stage & Commit**:
   - `git add .`
   - `git commit -m "[#Ticket] Beskrivning"`
3. **Verify**: QA kör `tests/` och rapporterar status.
4. **Report**: Summera ändringar.

## 3. TDD Protocol
- Varje ticket KRÄVER ett test i `tests/`.
- Ticketen är inte DONE förrän `verify_*.py` är grön.
- Om ett test misslyckas: RCA (Root Cause Analysis) -> Fix -> Commit.
