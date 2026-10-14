from kenya_health_mcp import server

_fn = lambda name: (getattr(server, name).fn if hasattr(getattr(server, name), "fn") else getattr(server, name))


def test_the_nhif_name_is_a_deprecated_alias_that_returns_the_shif_figure():
    a, b = _fn("get_nhif_contribution")(100000), _fn("get_shif_contribution")(100000)
    assert "deprecated" in a and a["employee_contribution_kes"] == b["employee_contribution_kes"] == 2750.0
    assert _fn("get_shif_contribution")(1000)["employee_contribution_kes"] == 300.0  # the KES 300 minimum
