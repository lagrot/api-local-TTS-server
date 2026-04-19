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

## Långsiktig Projektplan
1. **Pilot: Piper TTS** (Sprint 5) - Utvärdera prestanda och GPU-stabilitet.
2. **Kvalitetslyft (Fidelity)** (Sprint 6) - Utvärdera XTTS v2 eller liknande för high-fidelity/röstkloning.
3. **Produktionsstabilitet** (Sprint 7) - Fullt stöd för flertrådad inferens och caching.

## [2026-04-19] Beslut: Fokus Sprint 5
- [ ] **Ticket #12: Pilot Piper.** Integrera Piper som tredje alternativ i TTSLoaderFactory.

## Långsiktig Projektplan (Reviderad)
1. **Pilot: Piper TTS (Sprint 5)** - Snabb, GPU-vänlig, låg latens.
2. **High-Fidelity Motor (Sprint 6-7)** - Utvärdering av XTTS v2 eller VITS-baserade modeller med "Radio-kvalitet".
3. **Produktionsstabilitet (Sprint 8)** - Caching-lager, API-optimering för streaming och flertrådad inferens.

## [2026-04-19] Sprint 5 Slutrapport
- [x] **Ticket #12: Pilot Piper.** (KLAR: Integrerad via TTSLoaderFactory, verifierad med svensk röst).

## [2026-04-19] Sprint 6 Planering (High Fidelity)
- [ ] **Ticket #13: Implementera High-Fidelity Motor (Radio Quality).**
  - #13.1: Modellutvärdering (XTTS v2).
  - #13.2: Engine-implementation (XTTSLoader).
  - #13.3: Kvalitetstuning.
  - #13.4: Prestanda-benchmarking.

## [2026-04-19] Sprint 6 Status
- [x] **Ticket #13.1 & #13.2: Fish Speech Integration.** (KLAR: Installerad, GPU-verifierad och integrerad i TTSLoaderFactory).

## [2026-04-19] Sprint 6: Test-refaktorering
- [x] **Refaktorering av integrationstester:** Modulär testsvit () ersätter .

## Sprint 7 Backlog: Teknisk Optimering & Professionalisering
- [ ] **Ticket #14: Test-optimering (Fixtures & Conftest).** Implementera 'tests/conftest.py' för att dela modell-instanser mellan tester och dramatiskt öka testfarten.
- [ ] **Ticket #15: Dynamisk Loader-arkitektur.** Refaktorera 'TTSLoaderFactory' till att använda 'importlib' för att undvika "monolit-imports" i 'main.py'.
- [ ] **Ticket #16: Dokumentationsuppdatering.** Dokumentera nödvändiga systembibliotek (portaudio, ffmpeg) i 'HARDWARE.md' för att underlätta framtida miljöuppsättningar.
- [ ] **Ticket #17: Refaktorering av FFmpeg-pipeline.** Byta ut 'subprocess.Popen' i 'main.py' mot en stabilare lösning (t.ex. 'ffmpeg-python' eller förbättrad felhantering).

## [2026-04-19] Sprint 7 Status
- [x] **Ticket #14: Test-optimering.** (KLAR: conftest.py införd, snabbare testkörning).
- [x] **Ticket #15: Dynamisk Loader-arkitektur.** (KLAR: main.py refaktorerad för dynamisk init).

## [2026-04-19] Sprint 7 Status
- [x] **Ticket #16: Dokumentationsuppdatering.** (KLAR: Systemberoenden dokumenterade i HARDWARE.md).

## [2026-04-19] Sprint 7 Status (Hardening & Optimering)
- [x] **Ticket #14: Test-optimering (Conftest & Mocks).** (KLAR: Snabbare tester, isolerad logik).
- [x] **Ticket #15: Dynamisk Loader.** (KLAR: Robust main.py).
- [x] **Ticket #16: Dokumentation.** (KLAR: Systemberoenden i HARDWARE.md).
- [x] **Ticket #17: FFmpeg-pipeline.** (KLAR: Asynkrona subprocesses med timeouts).

## [2026-04-19] Sprint 7 Slutrapport
- [x] **Ticket #14: Test-optimering.** (KLAR: conftest.py, Mock-tester).
- [x] **Ticket #15: Dynamisk Loader.** (KLAR: robust main.py).
- [x] **Ticket #16: Dokumentation.** (KLAR: HARDWARE.md).
- [x] **Ticket #17: FFmpeg-pipeline.** (KLAR: Asynkron, timeout-skyddad, MP3-verifierad).

## [2026-04-19] Rensa bort Silero
- [x] **Ticket #18: Radera alla Silero-referenser.** (KLAR: Helt borttaget från src, tests och minne).
