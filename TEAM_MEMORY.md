# TEAM MEMORY – Kuraterad långsiktig kunskap

**Senast uppdaterad:** 2026-04-18

## Aktuell Backlog (Sprint 2)
- [x] **Ticket #6: Ollama-klient.** Implementera modul för Ollama-kommunikation.
- [ ] **Ticket #7: Orchestration.** Skapa `/chat`-endpoint som kedjar LLM + TTS.
- [ ] **Ticket #8: Integrationstest.** Validera hela "röst-samtals-kedjan".

## Arkitektur & Designbeslut
- KISS-principen: Minimala beroenden, fokus på funktionalitet.
- Hybrid-infrastruktur: Ollama (LLM) + Meta MMS (TTS).
- Device Agnostic: Koden använder `self.device = "cuda" if torch.cuda.is_available() else "cpu"`.

## Viktiga Fakta & Konventioner
- Namngivning: snake_case för Python-filer och variabler.
- Testning: Varje ticket kräver ett `tests/verify_*.py`.
- Commits: Conventional Commits.
- GitOps: Alla ändringar commitas direkt.

## Lärdomar & Gotchas
- [2026-04-18] Python 3.13 saknar `audioop` (inbyggt), vilket bryter `pydub`. Använd `ffmpeg`.
- [2026-04-18] `pytest.ini` med `pythonpath = .` löser import-problem.
- [2026-04-18] Ollama modellnamn måste matcha exakt enligt `http://localhost:11434/api/tags`.

## Godkända Ändringar
- 2026-04-18 [SCRUM MASTER] – Initialt repository, setup och dokumentation.
- 2026-04-18 [LEAD ENGINEER] – Implementerad MMSLoader och tillhörande QA-test.
- 2026-04-18 [LEAD ENGINEER] – Implementerat FastAPI-skelett och hälso-test.
- 2026-04-18 [LEAD ENGINEER] – Implementerad /tts-endpoint och QA-verifiering.
- 2026-04-18 [LEAD ENGINEER] – Implementerad OllamaClient.

## Definition of Done (DoD)
1. Kod commitad med konventionell commit-message.
2. `verify_*.py` testexekvering är grön.
3. QA Engineer har verifierat funktionaliteten.
