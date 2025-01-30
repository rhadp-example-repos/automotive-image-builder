from aib.vm import no_subcommand


def test_no_subcommand(caplog):
    no_subcommand("")
    assert "No subcommand specified" in caplog.text
