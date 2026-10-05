"""SHIF replaced NHIF in October 2024. The package used to return the old NHIF band table (capped at KES 1,700) and a doubled employer 'match', and also advertised
the NHIF-era 'Linda Mama free maternity' scheme as current. Expected values below are hand-computed from 2.75% of gross with a KES 300 minimum and no cap."""
import pytest

from kenya_health_mcp import server


@pytest.mark.parametrize("gross,expected", [(20000, 550.0), (100000, 2750.0), (250000, 6875.0), (12345.67, 339.51), (5000, 300.0), (10909, 300.0), (1, 300.0)])
def test_shif_is_2_75_percent_with_a_300_minimum_and_no_cap(gross, expected):
    assert server.get_shif_contribution(gross)["employee_contribution_kes"] == expected


def test_there_is_no_employer_match_and_the_total_is_the_employee_amount():
    r = server.get_shif_contribution(50000)
    assert r["employee_contribution_kes"] == 1375.0 and r["employer_match_kes"] == 0.0 and r["total_monthly_kes"] == 1375.0


def test_the_old_nhif_cap_is_gone():
    assert server.get_shif_contribution(1_000_000)["employee_contribution_kes"] == 27500.0  # the NHIF table topped out at 1,700


@pytest.mark.parametrize("bad", [0, -5000])
def test_non_positive_salary_is_an_error_not_a_contribution(bad):
    assert "error" in server.get_shif_contribution(bad)


def test_the_deprecated_name_returns_the_same_corrected_numbers_and_says_it_is_deprecated():
    old, new = server.get_nhif_contribution(20000), server.get_shif_contribution(20000)
    assert old["employee_contribution_kes"] == new["employee_contribution_kes"] == 550.0 and "deprecated" in old


def test_the_repealed_nhif_table_is_not_in_the_module():
    assert not hasattr(server, "NHIF_RATES")


def test_maternity_text_no_longer_promises_free_delivery_at_all_public_facilities():
    p = server.get_maternal_protocol()
    text = (p["programme"] + p["coverage"]).lower()
    assert "all public facilities" not in text and "registration" in text and "sha" in text


def test_mcp_dependency_is_pinned_below_2():
    """mcp 2.x removed mcp.server.fastmcp, so an unbounded 'mcp>=1.0.0' made a fresh install unable to import this server."""
    import pathlib
    import re

    pyproject = (pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    spec = re.search(r'"(mcp[<>=!~][^"]*)"', pyproject)  # a dependency string (has a version operator), not the "mcp" keyword
    assert spec and re.search(r"<\s*2", spec.group(1)), f"mcp must be pinned below 2, found {spec.group(1) if spec else None}"
