# Branching Narrative Train Game

This is a compact, Telltale-inspired interactive fiction where every choice nudges the crew of a battered train toward hope, distrust, or isolation. Run it interactively or script a path of choices to explore different endings.

## Running the game

```bash
python narrative_game.py
```

## Simulating predetermined choices

Choices are zero-indexed when scripted. For example, this path answers a distress call and brings survivors aboard:

```bash
python - <<'PY'
from narrative_game import NarrativeGame

result = NarrativeGame().simulate_path([1, 0, 0])
print(result)
PY
```

## Tests

```bash
python -m pytest
```
