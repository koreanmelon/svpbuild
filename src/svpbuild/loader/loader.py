"""
Handles discovering and loading assets, dependencies, and patches from the filesystem.

This module scans the source directory to build an in-memory representation of
all available expansions and character portraits before the builder compiles them.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from svpbuild.loader.character import CharacterLoader
from svpbuild.schemas import CPContentSpec, SMAPIManifest


class Loader:
    """
    Stateful asset loader that discovers and caches Stardew Valley mod assets.
    """

    def __init__(self, root: Path):
        """
        Scans the given source directory and loads the manifest, expansions,
        character assets, variants, dependencies, and patches into memory.
        """

        self.root: Path = root
        self.manifest: SMAPIManifest = self._load_manifest(root)
        self.characters = CharacterLoader(self.root.joinpath("assets"))

    def _load_manifest(self, root: Path) -> SMAPIManifest:
        manifest = root.joinpath("manifest.json")
        if not manifest.exists():
            raise FileNotFoundError(f"manifest.json not found in {root}")
        manifest_data = json.loads(manifest.read_text())
        manifest_data["$schema"] = "https://smapi.io/schemas/manifest.json"
        logging.debug(
            f"Loaded manifest for '{manifest_data.get('Name')}' ({manifest_data.get('UniqueID')})"
        )
        return manifest_data

    def build_config(self) -> dict[str, str]:
        return {name: "Standard" for name in self.characters.get_names()}

    def build_content(self) -> CPContentSpec:
        changes = []
        for character in self.characters.get_characters():
            for portrait in character.portraits:
                when_conditions: dict[str, str | int | bool] = {character.name: portrait.variant}
                when_conditions.update(portrait.conditions)

                changes.append(
                    {
                        "Action": "EditImage",
                        "Target": f"Portraits/{character.name}",
                        "FromFile": f"assets/{portrait.path}",
                        "Update": "OnDayStart",
                        "When": when_conditions,
                    }
                )

        content: CPContentSpec = {
            "$schema": "https://smapi.io/schemas/content-patcher.json",
            "Format": "2.9.0",
            "ConfigSchema": {
                character.name: {
                    "AllowValues": ", ".join(character.variants),
                    "Default": "Standard",
                }
                for character in self.characters.get_characters()
            },
            "Changes": changes,
        }

        character_count = len(list(self.characters.get_names()))
        logging.debug(
            "Generated %s patch(es) across %s character(s).",
            len(changes),
            character_count,
        )
        return content
