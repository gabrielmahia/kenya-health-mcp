import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_the_package_description_does_not_present_nhif_as_current_or_embed_a_tool_count():
    """NHIF was replaced by SHA/SHIF in October 2024; a count in a description goes stale."""
    desc = re.search(r'^description\s*=\s*"([^"]*)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE).group(1)
    assert "NHIF" not in desc or any(w in desc for w in ("successor", "replaced", "formerly")), desc
    assert not re.search(r"\b\d+ tools?\b", desc), desc
