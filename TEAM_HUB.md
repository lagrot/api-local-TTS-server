### [2026-04-18 10:00] [SCRUM MASTER] → [TEAM]
**Status:** Inleder projektets första stand-up för att definiera backlog och sprint-mål.  
**Observation:** Projektet startas om enligt KISS-principen.  
**Beslut / Förslag:** Vi bygger en ren, minimal och robust tjänst för Meta MMS TTS.  
**Action:** Initierat ny katalog och plan för Sprint 1.  

---
### Plan för Sprint 1 (KISS-MVP)
1. **Ticket #1: Setup & Dependencies.** (KLAR)
2. **Ticket #2: MMS Model Loader.** (PÅBÖRJAS)
3. **Ticket #3: Basic API Skeleton.** (FASTAPI + /health)
4. **Ticket #4: TTS Synthesis Endpoint.** (Integration + Ljudfilsoutput)
5. **Ticket #5: Sprint Review & Cleanup.** (QA-validering av hela kedjan)

---
### [2026-04-18 12:00] [SCRUM MASTER] → [TEAM]
**Status:** Ticket #1 är genomförd (Miljö verifierad).  
**Observation:** Vi har nu en ren KISS-baserad miljö och dokumentation på plats.  
**Beslut / Förslag:** Sprint 1 fokuserar på att bygga en minimal, fungerande TTS-pipeline.  
**Action:** Planera resterande tickets i Sprint 1.  
**Nästa steg:** Lead Python Engineer påbörjar Ticket #2 (MMS Model Loader).

---
### [2026-04-18 12:45] [LEAD ENGINEER] → [ALLA]
**Status:** Ticket #2 är genomförd.  
**Observation:** `MMSLoader` är implementerad och validerad via `tests/verify_mms.py`.  
**Beslut / Förslag:** Vi går vidare till Ticket #3 (API Skeleton).  
**Action:** Lead Engineer committade implementationen.  
**Nästa steg:** QA Engineer markerar Ticket #2 som DONE.

---
### [2026-04-18 13:45] [LEAD ENGINEER] → [ALLA]
**Status:** Ticket #3 är genomförd.  
**Observation:** FastAPI-servern är uppe med en `/health`-endpoint.  
**Beslut / Förslag:** Vi går vidare till Ticket #4 (TTS Endpoint).  
**Action:** Lead Engineer committade implementationen.  
**Nästa steg:** QA Engineer markerar Ticket #3 som DONE.
