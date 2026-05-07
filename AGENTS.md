# Claude Code Dos and Don'ts

## Git & Commits

- **DO** use descriptive commit messages. Never write jokes or placeholder text.
- **DON'T** add `Co-Authored-By` or any attribution trailers.
- **DON'T** force push without asking first (unless fixing a versioning mistake).
- **DON'T** amend published commits unless fixing a critical error.
- **DO** confirm before any destructive git operation (reset, force push, checkout --).

## Versioning

- **DO** always bump the **minor** version when PyPI is involved. e.g. 0.5.0 → 0.6.0, not 0.5.1.
- **DON'T** go backwards — a lower version can never be published after a higher one on PyPI.
- **DO** keep GitHub release tag in sync with PyPI version.

## Code Changes

- **DON'T** checkout or revert working code without explicit permission. This can destroy features.
- **DO** keep your changes scoped to what the user asked. No extras, no marketing language.
- **DON'T** add promotional descriptions like "Chainable • Gradient fills • 30+ effects" — that's marketing, not documentation.
- **DO** use `Path(__file__).parent` for asset paths in examples so they work from any CWD.

## Assets & Examples

- **DON'T** create assets outside `examples/assets/`. Root-level `assets/` is wrong.
- **DON'T** create new example files unless user explicitly asks for new ones.
- **DON'T** submit designs for approval without showing the user first. They will reject bad layouts.
- **DO** keep example files consistent in naming convention with existing ones.

## General

- **DON'T** be too proactive — wait for explicit instructions before committing, pushing, or making structural changes.
- **DO** verify all examples run before declaring success.
- **DO** ask when unsure instead of guessing.
- **DON'T** assume you know the user's intent. If unclear, ask.
