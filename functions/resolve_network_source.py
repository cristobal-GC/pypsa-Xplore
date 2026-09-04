

##### Identity of each network-building rule: filename template, storage location and
##### region tag used to load the matching regions_*.geojson files.
_RULES = {
    "base_network": {
        "filename": "base.nc",
        "location": "resources",
        "region_tag": "",
    },
    "simplify_network": {
        "filename": "base_s.nc",
        "location": "resources",
        "region_tag": "base_s",
    },
    "cluster_network": {
        "filename": "base_s_{clusters}.nc",
        "location": "resources",
        "region_tag": "base_s_{clusters}",
    },
    "add_electricity": {
        "filename": "base_s_{clusters}_elec.nc",
        "location": "resources",
        "region_tag": "base_s_{clusters}",
    },
    "prepare_network": {
        "filename": "base_s_{clusters}_elec_{opts}.nc",
        "location": "resources",
        "region_tag": "base_s_{clusters}",
    },
    "prepare_sector_network": {
        "filename": "base_s_{clusters}_{opts}_{sector_opts}_{horizon}.nc",
        "location": "resources",
        "region_tag": "base_s_{clusters}",
    },
    "solve_sector_network": {
        "filename": "base_s_{clusters}_{opts}_{sector_opts}_{horizon}.nc",
        "location": "results",
        "region_tag": "base_s_{clusters}",
    },
}


def resolve_network_source(
    rule: str,
    clusters=5,
    opts: str = "",
    sector_opts: str = "",
    horizon: str = "",
) -> dict:
    """Resolve the network file for a given PyPSA workflow rule.

    Given one of the 7 network-building rules and the run wildcards, return the
    information needed to load the corresponding network and its region files:

    Returns
    -------
    dict with keys:
        filename   : name of the .nc network file
        location   : "resources" or "results" (folder under rootpath)
        region_tag : tag for regions_onshore_<tag>.geojson (empty for base_network)

    The returned values feed directly into ``load_network`` and ``load_regions``.
    """
    if rule not in _RULES:
        valid = ", ".join(_RULES)
        raise ValueError(f"Unknown rule '{rule}'. Valid rules are: {valid}")

    spec = _RULES[rule]
    fields = {
        "clusters": clusters,
        "opts": opts,
        "sector_opts": sector_opts,
        "horizon": horizon,
    }

    return {
        "filename": spec["filename"].format(**fields),
        "location": spec["location"],
        "region_tag": spec["region_tag"].format(**fields),
    }
