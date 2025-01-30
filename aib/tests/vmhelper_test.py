import pytest

from aib import vmhelper


def test_print_error(capsys):
    vmhelper.print_error("test")
    captured = capsys.readouterr()
    assert captured.err == "test\n"


def test_exit_error(capsys):
    with pytest.raises(SystemExit) as expected:
        vmhelper.exit_error("test")
    assert expected.type == SystemExit
    assert expected.value.code == 1
    captured = capsys.readouterr()
    assert captured.err == "Error: test\n"


def test_runcmd(caplog, capsys):
    vmhelper.runcmd(["/usr/bin/true"])
    with pytest.raises(SystemExit) as expected:
        vmhelper.runcmd(["/usr/bin/false"])
    assert "Running: /usr/bin/false" in caplog.text
    assert expected.type == SystemExit
    assert expected.value.code == 1
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""
    with pytest.raises(SystemExit) as expected:
        vmhelper.runcmd(["/usr/bin/this_does_not_exist"])
    assert expected.type == SystemExit
    assert expected.value.code == 1
    captured = capsys.readouterr()
    assert captured.err == ""
    assert (
        captured.out
        == "Required program '/usr/bin/this_does_not_exist' missing, please install.\n"
    )


def test_goarch():
    assert vmhelper.goarch("x86_64") == "amd64"
    assert vmhelper.goarch("aarch64") == "arm64"
    # any other string pass-trough unmodified
    assert vmhelper.goarch("test") == "test"
