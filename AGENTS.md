# svpbuild - Technical Summary & Agent Context

This document captures the key architectural decisions, conventions, and workflows established for the `svpbuild` project, an automatic Stardew Valley Content Patcher portrait mod builder.

## 1. Directory Structure & File Discovery

- **Total Flexibility:** The `CharacterLoader` uses `pathlib.Path.rglob("*.png")` inside the `assets/` directory. It completely ignores folder names (like `Season/` or `Vanilla/`), allowing users to organize their images however they want.
- **Exact Pathing:** Instead of relying on generic Content Patcher template paths and `HasFile` checks, the loader calculates and stores the exact relative path for every single `.png` file. The final `content.json` points directly to these valid files.

## 2. The "Dash Schema" & Hybrid Auto-Detection

To balance a user-friendly experience with robust condition parsing, we use the **Dash Schema**:

- **Format:** `CharacterName-[VariantSegment]-[Condition]-[ConditionValue].png`
- **Why Dashes?** Vanilla Stardew Valley assets and user mods frequently use underscores (`_`). Using dashes as the structural delimiter prevents collision and misparsing.
- **Variant Normalization:** Unrecognized segments are grouped to form the custom variant name. They are joined by spaces, and any internal underscores (`_`) are also converted to spaces.
    - _Example:_ `Abigail-Beach-Party_Outfit.png` becomes variant `"Beach Party Outfit"`.
- **Reserved Values:** Hardcoded keywords that map instantly to Content Patcher tokens without requiring the user to type the token name.
    - _Seasons:_ `Spring`, `Summer`, `Fall`, `Winter` -> `Season`
    - _Weather:_ `Sun`, `Rain`, `Storm`, `Snow`, `Wind`, `GreenRain` -> `Weather`
    - _Days:_ `Monday`, `Tuesday`, etc. -> `DayOfWeek`
    - _Outdoors:_ `Indoor` -> `IsOutdoors: False`, `Outdoor` -> `IsOutdoors: True`
- **Known Tokens:** A list of standard Content Patcher tokens (e.g., `LocationName`, `DayEvent`, `Time`). If one of these is found, the parser grabs the _next_ segment as its value.
- **Type Casting:** Token values are parsed strictly: `"true"`/`"false"` become Python booleans (`True`/`False`). Digits become integers (e.g., `14`), unless they start with a leading zero and are multi-digit (e.g., `"0600"`), which remain strings.

## 3. Data Structures (`src/svpbuild/loader/types.py`)

- `PortraitAsset`: Represents a single `.png` file. Contains its calculated `variant` (str), parsed `conditions` (`dict[str, str | int | bool]`), and exact relative `path` (str).
- `CharacterAsset`: Groups portraits by character. Contains the character `name` (str) and a list of `PortraitAsset` objects. Provides a `unique_variants` property to help construct the `ConfigSchema`.

## 4. Content Patcher Output

- The `Loader` dynamically builds `manifest.json`, `config.json`, and `content.json`.
- Both `manifest.json` and `content.json` output with valid `$schema` keys at the top for proper editor support.
- `When` conditions inside `Changes` perfectly mirror the extracted conditions + variant logic, outputting booleans and integers as native JSON types (without quotes).

## 5. Logging Conventions

- Uses Python's native `logging` module.
- Defaults to `INFO` level. Adding the `-v` or `--verbose` flag sets the level to `DEBUG`.
- Log timestamps strictly use the RFC3339 UTC format: `%Y-%m-%dT%H:%M:%SZ`.

## 6. Versioning & Release Workflow

- **Single Source of Truth:** The version is defined exclusively in `pyproject.toml`. The CLI extracts this at runtime using `importlib.metadata.version()`.
- **Manual Versioning:** Before running a release, manually bump `version` in `pyproject.toml`, run `uv lock`, update `CHANGELOG.md`, and commit those changes.
- **Manual Trigger Release:** Deployments are triggered manually from the GitHub Actions UI via `workflow_dispatch`. The workflow publishes exactly the committed `pyproject.toml` version and does not bump versions automatically.
- **Workflow Steps:**
    1. Reads the committed version from `pyproject.toml` and records the release commit SHA.
    2. Fails if the matching git tag, GitHub Release, TestPyPI version, or PyPI version already exists.
    3. Enforces `uv.lock` consistency with `uv lock --check`.
    4. Runs locked CI checks with `uv run --locked`, then builds after lockfile validation.
    5. Publishes the built artifacts to TestPyPI via OIDC Trusted Publishing.
    6. Smoke-tests the TestPyPI install with `uvx`.
    7. Publishes the same artifacts to PyPI via OIDC Trusted Publishing.
    8. Creates and pushes the git tag (`vX.Y.Z`) and creates the GitHub Release.
- **Partial Publish Recovery:** If TestPyPI or PyPI succeeds but a later release step fails, handle recovery manually before rerunning because the workflow intentionally blocks duplicate package versions.
