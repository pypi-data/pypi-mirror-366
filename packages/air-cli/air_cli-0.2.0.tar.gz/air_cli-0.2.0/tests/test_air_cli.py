from pathlib import Path

from air_cli.cli import html


def test_html():
    assert html(Path("input"), Path("public")) == 0
