import pytest

from aib.main import parse_args
from aib import AIBParameters


BASEDIR = "/tmp/automotive-image-builder"

@pytest.mark.parametrize("subcmd", [
    "list-dist",
    "list-targets",
    "compose",
    "build",
])
def test_valid_subcommands(subcmd):
    with pytest.raises(SystemExit) as e:
        parse_args([subcmd, "--help"], base_dir="")
    assert e.value.code == 0

def test_invalid_subcommand():
    with pytest.raises(SystemExit) as e:
        parse_args(["invalid", "--help"], base_dir="")
    assert e.value.code == 2

def test_no_subcommand(caplog):
    args = parse_args([], base_dir="")
    args.func(_args=args, _tmpdir="", _runner=None)
    assert "No subcommand specified, see --help for usage" in caplog.text

def test_build_required_positional(capsys):
    with pytest.raises(SystemExit) as e:
        parse_args(["build"], base_dir="")
    assert e.value.code == 2
    assert "error: the following arguments are required: manifest, out" in capsys.readouterr().err

@pytest.mark.parametrize("mpp_args,expected", [
    (["--mpp-arg=--cache", "--mpp-arg", "/path/to/cache"], ["--cache", "/path/to/cache"]),
    (["--mpp-arg=--cache", "--mpp-arg=/path/to/cache"], ["--cache", "/path/to/cache"]),
])
def test_build_mpp_arg(mpp_args, expected):
    args = parse_args(["build"] + mpp_args + ["manifest", "out"], base_dir="")
    assert args.mpp_arg == expected

def test_build_cache_arg():
    cache_path = "/path/to/cache"
    args = parse_args(["build", "--cache", cache_path, "manifest", "out"], base_dir="")
    assert args.cache == cache_path

@pytest.mark.parametrize("includes", [
    [],
    ["dir1"],
    ["dir1", "dir2"],
])
def test_aib_paramters(includes):
    base_dir = "base_dir"
    argv = []
    for inc in includes:
        argv.extend(["--include", inc])
    args = AIBParameters(args=parse_args(argv, base_dir), base_dir=base_dir)
    assert args.base_dir == base_dir
    assert args.include_dirs == [base_dir] + includes
