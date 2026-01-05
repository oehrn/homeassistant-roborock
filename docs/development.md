# Development notes

This repository is a Home Assistant **custom component** integration.

---

## Repo layout (relevant parts)

- `custom_components/roborock/` — integration code
- `docs/` — documentation
- `.github/workflows/` — CI (lint/validate/release)
- `ruff.toml` — lint rules

---

## Local linting

Ruff is used for linting.

Typical commands:
- `ruff check .`
- `ruff check --fix .` (only if you want auto-fixes)

---

## Contribution expectations

This repo is separate from Home Assistant Core.
If you are aiming for long-term stability or the newest feature work, Core is usually the better target.

For changes here:
- keep PRs small and focused
- include logs/repro steps when fixing bugs
- avoid large refactors unless clearly motivated
