# TEAM MEMORY – Kuraterad långsiktig kunskap

## Aktuell Backlog (Sprint 1)
- [x] **Ticket #1: Setup & Dependencies.** Initiera `pyproject.toml` och verifiera miljö. (QA-krav: `uv sync` lyckas och `torch` fungerar)
- [ ] **Ticket #2: MMS Model Loader.** Implementera modul för att ladda MMS-modellen. (QA-krav: Enhetstest verifierar att modellen laddas i minnet)
- [ ] **Ticket #3: Basic API Skeleton.** Implementera FastAPI-server med hälso-endpoint. (QA-krav: `curl localhost:8000/health` returnerar 200)
- [ ] **Ticket #4: TTS Endpoint.** Integrera MMS-loader i API-servern. (QA-krav: `/tts`-endpoint genererar en giltig ljudfil)

## Definition of Done (DoD)
1. Kod commitad med konventionell commit-message.
2. `verify_*.py` testexekvering är grön.
3. QA Engineer har verifierat funktionaliteten.
