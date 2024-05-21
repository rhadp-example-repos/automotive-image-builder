import pytest

from aib.main import parse_args


BASEDIR = "/tmp/automotive-image-builder"

@pytest.mark.parametrize("subcmd", [
    "list-dist",
    "list-targets",
    "compose",
    "build",
])
def test_valid_subcommands(subcmd):
    with pytest.raises(SystemExit) as e:
        parse_args([subcmd, "--help"])
    assert e.value.code == 0

def test_invalid_subcommand():
    with pytest.raises(SystemExit) as e:
        parse_args(["invalid", "--help"])
    assert e.value.code == 2

def test_no_subcommand(caplog):
    args = parse_args([])
    args.func(_args=args, _tmpdir="", _runner=None)
    assert "No subcommand specified, see --help for usage" in caplog.text

def test_build_required_positional(capsys):
    with pytest.raises(SystemExit) as e:
        parse_args(["build"])
    assert e.value.code == 2
    assert "error: the following arguments are required: manifest, out" in capsys.readouterr().err

@pytest.mark.parametrize("mpp_args,expected", [
    (["--mpp-arg=--cache", "--mpp-arg", "/path/to/cache"], ["--cache", "/path/to/cache"]),
    (["--mpp-arg=--cache", "--mpp-arg=/path/to/cache"], ["--cache", "/path/to/cache"]),
])
def test_build_mpp_arg(mpp_args, expected):
    args = parse_args(["build"] + mpp_args + ["manifest", "out"])
    assert args.mpp_arg == expected

def test_build_cache_arg():
    cache_path = "/path/to/cache"
    args = parse_args(["build", "--cache", cache_path, "manifest", "out"])
    assert args.cache == cache_path
