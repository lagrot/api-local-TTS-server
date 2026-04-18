# TEAM MEMORY – Kuraterad långsiktig kunskap

**Senast uppdaterad:** 2026-04-18

## Aktuell Backlog (Sprint 2)
- [ ] **Ticket #6: Ollama-klient.** Implementera modul för Ollama-kommunikation.
- [ ] **Ticket #7: Orchestration.** Skapa `/chat`-endpoint som kedjar LLM + TTS.
- [ ] **Ticket #8: Integrationstest.** Validera hela "röst-samtals-kedjan".

## Arkitektur & Designbeslut
- KISS-principen: Minimala beroenden, fokus på funktionalitet.
- Hybrid-infrastruktur: Ollama (LLM) + Meta MMS (TTS).
- Device Agnostic: Koden använder `self.device = "cuda" if torch.cuda.is_available() else "cpu"`.

## Viktiga Fakta & Konventioner
- Namngivning: snake_case för Python-filer och variabler.
- Testning: Varje ticket kräver ett `tests/verify_*.py`.
- GitOps: Alla ändringar commitas direkt.

## Lärdomar & Gotchas
- Använd `ffmpeg` för ljudkonvertering (MP3) då `pydub`/`audioop` är inkompatibelt med Python 3.13.
- `pytest.ini` med `pythonpath = .` löser import-problem.

## Godkända Ändringar
- 2026-04-18 [SCRUM MASTER] – Sprint 2 backlog och planering.

## Definition of Done (DoD)
1. Kod commitad med konventionell commit-message.
2. `verify_*.py` testexekvering är grön.
3. QA Engineer har verifierat funktionaliteten.
