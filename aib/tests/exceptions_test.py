import pytest

from aib.main import parse_args, create_osbuild_manifest, rewrite_manifest
from aib import AIBParameters
from aib import exceptions
from aib.exports import get_export_data


BASE_DIR = "/usr/lib/automotive-image-builder"
INVALID_YAML = """
  # Bad indentation
  pipelines:

qm_rootfs:
"""


def test_create_manifest(tmp_path):
    manifest_file = tmp_path / "manifest.yml"
    manifest_file.write_text(INVALID_YAML)
    args = AIBParameters(
        args=parse_args(
            ["compose", manifest_file.as_posix(), "output"], base_dir=BASE_DIR
        ),
        base_dir=BASE_DIR,
    )
    with pytest.raises(exceptions.ManifestParseError) as manifest_err:
        create_osbuild_manifest(args, tmpdir="/tmp", out="output", runner=None)
    assert manifest_file.as_posix() in str(manifest_err)


def test_rewrite_manifest():
    with pytest.raises(exceptions.MissingSection) as pipelines_err:
        rewrite_manifest({"pipelines": []}, "/mock/path")
    assert "pipelines" in str(pipelines_err)


def test_missing_export():
    with pytest.raises(SystemExit) as argparse_err:
        AIBParameters(args=parse_args(["build", "out"], BASE_DIR), base_dir=BASE_DIR)
    assert argparse_err.value.code == 2


def test_export_data():
    with pytest.raises(exceptions.UnsupportedExport) as export_err:
        get_export_data("ostre-commit")
    assert "ostre-commit" in str(export_err)
