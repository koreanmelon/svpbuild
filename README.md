# svpbuild

[![CI](https://github.com/koreanmelon/svpbuild/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/koreanmelon/svpbuild/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/svpbuild?label=PyPI)](https://pypi.org/project/svpbuild/)
[![Python Versions](https://img.shields.io/pypi/pyversions/svpbuild)](https://pypi.org/project/svpbuild/)
[![License](https://img.shields.io/pypi/l/svpbuild)](LICENSE)

Build Stardew Valley Content Patcher portrait packs without hand-writing `content.json`.

`svpbuild` scans a source folder, discovers portrait PNGs, parses variants and conditions from
filenames, and writes a ready-to-install Content Patcher content pack.

This project is not affiliated with, endorsed by, or maintained by ConcernedApe, SMAPI, or Content
Patcher.

## Usage

Run without installing permanently:

```sh
uvx svpbuild --help
uvx svpbuild ./my-portrait-pack -o ./build
```

Install as a persistent CLI tool:

```sh
uv tool install svpbuild
svpbuild --help
```

Other install options:

```sh
pipx install svpbuild
pip install svpbuild
```

## Source Layout

Your source directory must contain a SMAPI `manifest.json` and an `assets/` directory.

```text
my-portrait-pack/
  manifest.json
  assets/
    Abigail.png
    Abigail-Summer.png
    Abigail-Beach_Outfit-Rain.png
    Sebastian-Goth-LocationName-Saloon.png
```

Folders inside `assets/` are optional. `svpbuild` recursively discovers every `.png` file and uses
the exact relative path in the generated `content.json`.

```text
assets/
  seasonal/Abigail-Summer.png
  custom/Sebastian-Goth-LocationName-Saloon.png
```

## Filename Schema

Use dashes to separate structural filename segments:

```text
CharacterName-[VariantSegment]-[Condition]-[ConditionValue].png
```

Examples:

```text
Abigail.png                                  -> Abigail, Standard
Abigail-Summer.png                           -> Abigail, Standard, Season = Summer
Abigail-Beach_Outfit.png                     -> Abigail, Beach Outfit
Abigail-Beach_Outfit-Summer.png              -> Abigail, Beach Outfit, Season = Summer
Sebastian-Goth-LocationName-Saloon.png       -> Sebastian, Goth, LocationName = Saloon
```

Reserved condition values are detected automatically:

- Seasons: `Spring`, `Summer`, `Fall`, `Winter`
- Weather: `Sun`, `Rain`, `Storm`, `Snow`, `Wind`, `GreenRain`
- Days: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`
- Outdoors: `Indoor`, `Outdoor`

Known Content Patcher tokens consume the next segment as their value, for example
`LocationName-Saloon` or `Day-14`.

Unrecognized segments become the variant name. Underscores inside variants are converted to spaces.

## Output

By default, `svpbuild` writes a built content pack into `build/`:

```text
build/<UniqueID>-<Version>/
  manifest.json
  content.json
  config.json
  assets/
```

Use `-o` or `--output` to choose a different output directory.

```sh
svpbuild ./my-portrait-pack --output ./dist
svpbuild ./my-portrait-pack --verbose
svpbuild --version
```

## Development

```sh
uv run svpbuild --help
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev pytest
uv build
```

## Release

Releases are published from GitHub Actions with trusted publishing.

Before running the release workflow, manually bump `version` in `pyproject.toml`, run `uv lock`,
update `CHANGELOG.md`, and commit those changes. The release workflow publishes exactly the version
already committed to `pyproject.toml`; it does not bump versions automatically.

The workflow fails if the version already exists as a git tag, GitHub Release, TestPyPI release, or
PyPI release.

Configure these GitHub environments before the first release:

- `testpypi`
- `pypi`

Configure trusted publishers for `.github/workflows/release.yml` on both TestPyPI and PyPI.
