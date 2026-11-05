"""Live tools: parsing, provenance, validation and failure behaviour, with the network mocked (CI never depends on the services)."""
import urllib.error

from kenya_health_mcp import server


def _boom(url, params=None, timeout=20.0):
    raise urllib.error.URLError("down")

def test_dhs_indicator_national_and_county(monkeypatch):
    data = [{"Indicator": "Fully vaccinated", "Value": 80.1, "CharacteristicLabel": "Total", "ByVariableLabel": "", "CILow": 78.9, "CIHigh": 81.2},
            {"Indicator": "Fully vaccinated", "Value": 70.6, "CharacteristicLabel": "..Kwale", "ByVariableLabel": "", "CILow": None, "CIHigh": None}]
    seen = {}
    monkeypatch.setattr(server, "_live_get", lambda url, params=None, timeout=20.0: seen.update(params) or {"Data": data})
    r = server.dhs_health_indicator("full_vaccination")
    assert r["values"][0]["value"] == 80.1 and r["area"] == "Kenya" and seen["surveyIds"] == "KE2022DHS" and "breakdown" not in seen
    r = server.dhs_health_indicator("full_vaccination", "Kwale")
    assert r["values"][0]["value"] == 70.6 and seen["breakdown"] == "subnational" and "DHS" in r["attribution"]


def test_dhs_indicator_unknown_inputs_and_failures_never_give_figures(monkeypatch):
    monkeypatch.setattr(server, "_live_get", lambda url, params=None, timeout=20.0: {"Data": []})
    assert "error" in server.dhs_health_indicator("stunting", "Atlantis") and "error" in server.dhs_health_indicator("happiness")
    monkeypatch.setattr(server, "_live_get", _boom)
    assert "values" not in server.dhs_health_indicator("stunting")
