from kenya_health_mcp import server

fn = server.find_facility.fn if hasattr(server.find_facility, "fn") else server.find_facility


def test_no_unverified_emergency_number_and_no_registry_claim():
    """It listed 0800 720 021 as a free 24hr line (no source found), gave 0800 723 253 (a nonprofit's number) as an ambulance line, and called a hand-written sample the Ministry's registry."""
    r = fn("Nairobi")
    text = str(r)
    assert "0800 720 021" not in text and "723 253" not in text
    assert "999" in r["emergency"] and "112" in r["emergency"]
    assert "NOT the Kenya Master Health Facility List" in r["source"] and "registry" not in r["source"].lower().replace("master health facility list", "")
