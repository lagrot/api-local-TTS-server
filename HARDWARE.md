# Hardware & ROCm Configuration

## Hårdvarukrav
- **GPU**: AMD Radeon RX 6700 XT.
- **Drivrutiner (Linux)**: ROCm 7.2.1.
- **Drivrutiner (Windows)**: AMD Software: Adrenalin Edition.

## Platform Configuration
### Linux
- Kräver `HSA_OVERRIDE_GFX_VERSION=10.3.0` (sköts automatiskt av `LinuxAdapter`).

### Windows
- Använder `torch-directml` för acceleration på AMD-GPU:er.
- Vid avsaknad av DirectML eller kompatibel GPU sker automatisk fallback till CPU.

## Pre-flight Check
Servern kör en automatisk kontroll via `run_server.sh` vid start som verifierar:
1. Att `HSA_OVERRIDE_GFX_VERSION` är korrekt satt.
2. Att `torch.cuda.is_available()` returnerar True för AMD-GPU:n.

Vid fel avbryts startprocessen omedelbart för att förhindra körning på CPU (vilket är långsamt) eller systemkrascher.
