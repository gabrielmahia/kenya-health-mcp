"""Smoke tests for kenya-health-mcp."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from kenya_health_mcp.server import get_nhif_contribution, get_health_right, find_facility, get_maternal_protocol

def test_nhif_50k():
    r = get_nhif_contribution(50000)
    assert r["employee_contribution_kes"] == 1100
    assert r["total_monthly_kes"] == 2200

def test_nhif_85k():
    r = get_nhif_contribution(85000)
    assert r["employee_contribution_kes"] == 1500

def test_find_nairobi():
    r = find_facility("Nairobi")
    assert len(r["facilities"]) > 0

def test_find_unknown_county():
    r = find_facility("UnknownPlace")
    assert r["facilities"] == []

def test_health_right_en():
    r = get_health_right("healthcare", "en")
    assert "Article" in r.get("right", "")

def test_health_right_sw():
    r = get_health_right("maternal", "sw")
    assert "Kifungu" in r.get("right", "") or "Mpango" in r.get("right", "")

def test_maternal_protocol():
    r = get_maternal_protocol()
    assert len(r["antenatal_visits"]) == 6
