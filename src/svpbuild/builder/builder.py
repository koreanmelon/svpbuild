import json
import logging
import shutil
from pathlib import Path

from svpbuild.loader.loader import Loader

logger = logging.getLogger(__name__)


class Builder:
    """
    Handles the final construction of the mod output directory.
    Takes an in-memory Loader and writes the assets and JSON configurations to disk.
    """

    def __init__(self, loader: Loader, output_dir: Path):
        self.loader = loader
        self.output_dir = output_dir

    def build(self) -> Path:
        """Writes the loaded assets and JSON files to the output directory."""
        manifest_json = self.loader.manifest
        mod_id = manifest_json["UniqueID"]
        mod_version = manifest_json["Version"]

        mod_out_dir = self.output_dir.joinpath(f"{mod_id}-{mod_version}")
        logger.debug(f"Output directory resolved to: {mod_out_dir}")
        mod_out_dir.mkdir(parents=True, exist_ok=True)

        assets_src = self.loader.root.joinpath("assets")
        if assets_src.exists() and assets_src.is_dir():
            logger.debug("Copying assets directory...")
            shutil.copytree(
                src=assets_src,
                dst=mod_out_dir.joinpath("assets"),
                dirs_exist_ok=True,
            )

        logger.debug("Writing JSON configuration files...")
        mod_out_dir.joinpath("manifest.json").write_text(json.dumps(manifest_json, indent=4))
        mod_out_dir.joinpath("content.json").write_text(
            json.dumps(self.loader.build_content(), indent=4)
        )
        mod_out_dir.joinpath("config.json").write_text(
            json.dumps(self.loader.build_config(), indent=4)
        )

        return mod_out_dir
