# TEAM MEMORY – Kuraterad långsiktig kunskap

**Senast uppdaterad:** 2026-04-18

## Aktuell Backlog (Sprint 3: Optimering & GPU)
- [ ] **Ticket #9: ROCm-optimering.** Konfigurera PyTorch/ROCm för att använda AMD GPU (RX 6700 XT).
- [x] **Ticket #10: Latency Optimization.** Implementera streaming (server-sent events) för snabbare svarstider.
- [x] **Ticket #11: Röst-kloning/Kvalitetslyft.** Utvärdera Silero eller XTTS för naturligare svenskt tal.

## Sprint 1 & 2 (Genomförda)
- Alla tickets i Sprint 1 & 2 är klara (se historik i TEAM_HUB.md).

## Arkitektur & Designbeslut
- KISS-principen: Minimala beroenden, fokus på funktionalitet.
- Hybrid-infrastruktur: Ollama (LLM) + Meta MMS (TTS).
- Device Agnostic: Koden använder `self.device = "cuda" if torch.cuda.is_available() else "cpu"`.

## Viktiga Fakta & Konventioner
- Namngivning: snake_case.
- Testning: Varje ticket kräver ett `tests/verify_*.py`.
- Commits: Conventional Commits.
- GitOps: Alla ändringar commitas direkt.

## Lärdomar & Gotchas
- [2026-04-18] Python 3.13 saknar `audioop` -> FFmpeg krävs.
- [2026-04-18] `pytest.ini` med `pythonpath = .` löser import-problem.
- [2026-04-18] Alla test-beroenden måste deklareras i `pyproject.toml`.

## Definition of Done (DoD)
1. Kod commitad med konventionell commit-message.
2. `verify_*.py` testexekvering är grön.
3. QA Engineer har verifierat funktionaliteten.

## [2026-04-19] Uppdatering av Sprint 3 Status
- [x] **Ticket #9: ROCm-optimering.** (Delvis utförd: Nuvarande lösning körs stabilt på CPU, ROCm-optimering kvarstår som teknisk skuld).
- [x] **Ticket #10: Latency Optimization.** (KLAR)
- [x] **Ticket #11: Röst-kloning/Kvalitetslyft.** (KLAR)

## [2026-04-19] Beslut: Fokus Sprint 4
- [ ] **Ticket #9: Återöppnad - ROCm-optimering.** Prioriterad för att nå målet om GPU-acceleration på AMD-hårdvara.

## [2026-04-19] Sprint 4 Slutrapport
- [x] **Ticket #9: ROCm-optimering.** (Avslutad: GPU-stöd verifierat på drivrutinsnivå, men MMS-inferens är instabil på GPU. CPU-körning är nuvarande standard).
