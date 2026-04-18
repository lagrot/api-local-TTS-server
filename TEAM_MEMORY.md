# TEAM MEMORY – Kuraterad långsiktig kunskap

**Senast uppdaterad:** 2026-04-18

## Aktuell Backlog (Sprint 1)
- [x] **Ticket #1: Setup & Dependencies.** Initiera `pyproject.toml` och verifiera miljö.
- [x] **Ticket #2: MMS Model Loader.** Implementera modul för att ladda MMS-modellen. (QA-krav: Enhetstest verifierar att modellen laddas i minnet)
- [ ] **Ticket #3: Basic API Skeleton.** Implementera FastAPI-server med hälso-endpoint. (QA-krav: `curl localhost:8000/health` returnerar 200)
- [ ] **Ticket #4: TTS Endpoint.** Integrera MMS-loader i API-servern. (QA-krav: `/tts`-endpoint genererar en giltig ljudfil)
- [ ] **Ticket #5: Sprint Review & Cleanup.** QA-validering av hela kedjan.

## Arkitektur & Designbeslut
- KISS-principen (Keep It Simple, Stupid): Minimala beroenden, fokus på funktionalitet.
- Hybrid-infrastruktur: Ollama (LLM) + Meta MMS (TTS).

## Viktiga Fakta & Konventioner
- Namngivning: snake_case för Python-filer och variabler.
- Testning: Varje ticket kräver ett `tests/verify_*.py`.
- Commits: Conventional Commits.
- GitOps: Alla ändringar commitas direkt efter QA-godkännande.

## Lärdomar & Gotchas
- Miljökonfigurationer (Python 3.10 vs 3.12) kan orsaka dependency hell; håll miljön strikt.
- Verifiera alltid `torch` via `.venv/bin/python`.
- Python-import-fel fixas genom `pytest.ini` med `pythonpath = .`.
- Alla test-beroenden (t.ex. `pytest`) måste explicit deklareras i `pyproject.toml`.

## Godkända Ändringar
- 2026-04-18 [SCRUM MASTER] – Initialt repository, setup och dokumentation.
- 2026-04-18 [LEAD ENGINEER] – Implementerad MMSLoader och tillhörande QA-test.

## Definition of Done (DoD)
1. Kod commitad med konventionell commit-message.
2. `verify_*.py` testexekvering är grön.
3. QA Engineer har verifierat funktionaliteten.
