# Release Recovery

The release workflow publishes the same built artifacts to TestPyPI, smoke-tests the TestPyPI install, publishes to PyPI, then creates the git tag and GitHub Release.

This ordering avoids tagging a version before the package is successfully published, but it means reruns can be blocked after a partial publish. The workflow intentionally fails if the version already exists on TestPyPI, PyPI, as a git tag, or as a GitHub Release.

## Failure Cases

### TestPyPI Publish Succeeds, Later Step Fails

If TestPyPI publish succeeds but the smoke test, PyPI publish, tag creation, or GitHub Release step fails, rerunning the workflow with the same version may fail because TestPyPI already has that version.

Recovery options:

1. If PyPI was not published, bump `version` in `pyproject.toml`, run `uv lock`, update `CHANGELOG.md`, commit, and rerun the workflow.
2. If the TestPyPI package is acceptable but the smoke test failed due to indexing delay or infrastructure, verify manually before deciding whether to release a new version.

### PyPI Publish Succeeds, Tag Or GitHub Release Fails

If PyPI publish succeeds but tag creation or GitHub Release creation fails, do not bump the version just to recover metadata.

Recover manually:

1. Verify the package exists on PyPI.
2. Create and push the matching tag from the release commit: `git tag vX.Y.Z <release-commit-sha>` and `git push origin vX.Y.Z`.
3. Create the GitHub Release for that tag: `gh release create vX.Y.Z --title vX.Y.Z --generate-notes`.

### GitHub Release Exists But Later Metadata Needs Fixing

If the GitHub Release exists but its notes or title are wrong, edit the release manually in GitHub or with `gh release edit`.

## Before Rerunning

Before rerunning the workflow, check which release artifacts already exist:

- Git tag: `git ls-remote --tags origin refs/tags/vX.Y.Z`
- GitHub Release: `gh release view vX.Y.Z`
- PyPI: `https://pypi.org/project/svpbuild/X.Y.Z/`
- TestPyPI: `https://test.pypi.org/project/svpbuild/X.Y.Z/`

Only rerun with the same version if none of the package indexes already contain that version.

## Normal Release Checklist

1. Bump `version` in `pyproject.toml`.
2. Run `uv lock`.
3. Update `CHANGELOG.md`.
4. Commit the release prep changes.
5. Trigger the GitHub Actions release workflow.
