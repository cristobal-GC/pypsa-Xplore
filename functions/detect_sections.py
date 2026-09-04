

import pypsa


def _has_static(n: pypsa.Network, component: str) -> bool:
    """True if a static component dataframe (e.g. 'generators') has any row."""
    df = getattr(n, component, None)
    return df is not None and not df.empty


def _has_varying(n: pypsa.Network, component_t: str, key: str) -> bool:
    """True if a time-varying entry (e.g. generators_t['p']) exists and is not empty."""
    container = getattr(n, component_t, None)
    if container is None or key not in container:
        return False
    return not container[key].empty


def detect_sections(n: pypsa.Network) -> dict:
    """Inspect a loaded network and report which analysis sections make sense.

    The unified ``Xplore_networks/network.ipynb`` uses these flags to run only the
    sections whose components actually exist, so the same notebook works for any
    intermediate/final network state and for any spatial domain (ES, EU, ...).

    Returns a dict of booleans keyed by section name.
    """
    sections = {
        # static components
        "generators": _has_static(n, "generators"),
        "lines": _has_static(n, "lines"),
        "links": _has_static(n, "links"),
        "loads": _has_static(n, "loads"),
        "storage_units": _has_static(n, "storage_units"),
        "stores": _has_static(n, "stores"),
        "shapes": _has_static(n, "shapes"),
        "transformers": _has_static(n, "transformers"),
        "global_constraints": _has_static(n, "global_constraints"),
        # time-varying components
        "pmaxpu": _has_varying(n, "generators_t", "p_max_pu"),
        "loads_t": _has_varying(n, "loads_t", "p_set"),
        # a solved network exposes optimal dispatch (generators_t['p'])
        "solved": _has_varying(n, "generators_t", "p"),
    }

    # Interconnections analysis (PyPSA-Spain): border links named *export*/*import*
    sections["interconnections"] = (
        sections["links"] and bool(n.links.index.str.contains("export").any())
    )

    return sections
