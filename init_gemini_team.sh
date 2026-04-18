#!/bin/bash
# init_gemini_team.sh
# Skapar TEAM_HUB.md, TEAM_MEMORY.md och TEAM_MEMORY.json

set -e  # Avbryt vid fel

echo "🔧 Skapar Gemini Team-filer..."

# Skapa TEAM_HUB.md
cat > TEAM_HUB.md << 'EOF_HUB'
# TEAM HUB – Gemensamt chatt och operational minne

**Senast uppdaterad:** $(date '+%Y-%m-%d %H:%M')

*(Alla agenter skriver här med den strikta mallen nedan)*
EOF_HUB

# Skapa TEAM_MEMORY.md
cat > TEAM_MEMORY.md << 'EOF_MEM'
# TEAM MEMORY – Kuraterad långsiktig kunskap

**Senast uppdaterad:** $(date '+%Y-%m-%d')

## Arkitektur & Designbeslut
- (Lägg till godkända beslut här)

## Viktiga Fakta & Konventioner
- (Projekt-specifika regler och sanningar)

## Lärdomar & Gotchas
- (Vad vi lärt oss av misstag)

## Godkända Ändringar
- [YYYY-MM-DD] [AGENT] – Kort beskrivning (länk till commit vid behov)
EOF_MEM

# Skapa TEAM_MEMORY.json
cat > TEAM_MEMORY.json << 'EOF_JSON'
{
  "last_updated": "$(date '+%Y-%m-%d')",
  "project_name": "Gemini Project",
  "decisions": [],
  "conventions": {
    "naming": "snake_case för Python-filer och variabler",
    "testing": "Varje ticket kräver verify_*.py",
    "commits": "Conventional Commits"
  },
  "architecture": {}
}
EOF_JSON

echo "✅ Filer skapade."
