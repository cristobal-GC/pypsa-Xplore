##### Identity of each network-building rule of the streamlined workflow
##### (PyPSA-Eur #1838: base → simplified → clustered → composed → solved):
##### filename template, storage location and the onshore/offshore region files.
##### The wildcards clusters/opts/sector_opts are gone (they are config-driven now);
##### only {horizon} remains, for the composed/solved networks.
_RULES = {
    "base_network": {
        "filename": "base.nc",
        "location": "resources",
        "regions": "base",
    },
    "simplify_network": {
        "filename": "simplified.nc",
        "location": "resources",
        "regions": "simplified",
    },
    "cluster_network": {
        "filename": "clustered.nc",
        "location": "resources",
        "regions": "",
    },
    "compose_network": {
        "filename": "composed_{horizon}.nc",
        "location": "resources",
        "regions": "",
    },
    "solve_network": {
        "filename": "solved_{horizon}.nc",
        "location": "results",
        "regions": "",
    },
    "solve_operations_network": {
        "filename": "operations_{horizon}.nc",
        "location": "results",
        "regions": "",
    },
}


def resolve_network_source(rule: str, horizon: str = "") -> dict:
    """Resolve the network file for a given PyPSA workflow rule.

    Given one of the network-building rules and the planning horizon, return the
    information needed to load the corresponding network and its region files.

    Returns
    -------
    dict with keys:
        filename         : name of the .nc network file
        location         : "resources" or "results" (folder under rootpath)
        regions_onshore  : onshore regions file (onshore_regions[_<suffix>].geojson)
        regions_offshore : offshore regions file (offshore_regions[_<suffix>].geojson)

    The returned values feed directly into ``load_network`` and ``load_regions``.
    """
    if rule not in _RULES:
        valid = ", ".join(_RULES)
        raise ValueError(f"Unknown rule '{rule}'. Valid rules are: {valid}")

    spec = _RULES[rule]
    if "{horizon}" in spec["filename"] and not horizon:
        raise ValueError(f"Rule '{rule}' needs a planning horizon (e.g. horizon='2030').")

    suffix = f"_{spec['regions']}" if spec["regions"] else ""

    return {
        "filename": spec["filename"].format(horizon=horizon),
        "location": spec["location"],
        "regions_onshore": f"onshore_regions{suffix}.geojson",
        "regions_offshore": f"offshore_regions{suffix}.geojson",
    }
