import json

import pytest

from svpbuild.builder import Builder
from svpbuild.loader import Loader
from svpbuild.main import main


def test_builder_writes_content_pack(sample_pack_dir, tmp_path):
    loader = Loader(sample_pack_dir)
    output_dir = tmp_path / "dist"

    mod_out_dir = Builder(loader, output_dir).build()

    assert mod_out_dir == output_dir / "Test.SamplePortraits-1.0.0"
    assert (mod_out_dir / "assets" / "Abigail" / "Abigail.png").exists()

    manifest = json.loads((mod_out_dir / "manifest.json").read_text())
    content = json.loads((mod_out_dir / "content.json").read_text())
    config = json.loads((mod_out_dir / "config.json").read_text())

    assert manifest["$schema"] == "https://smapi.io/schemas/manifest.json"
    assert content["$schema"] == "https://smapi.io/schemas/content-patcher.json"
    assert config == {"Abigail": "Standard", "Sebastian": "Standard"}


def test_cli_builds_sample_pack(sample_pack_dir, tmp_path, monkeypatch):
    output_dir = tmp_path / "build"
    monkeypatch.setattr("sys.argv", ["svpbuild", str(sample_pack_dir), "-o", str(output_dir)])

    main()

    assert (output_dir / "Test.SamplePortraits-1.0.0" / "content.json").exists()


def test_cli_missing_manifest_exits_cleanly(tmp_path, monkeypatch):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    monkeypatch.setattr("sys.argv", ["svpbuild", str(source_dir)])

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 1
