"""Choropleth maps of network components over the onshore/offshore regions.

Every public ``map_network_*`` function builds a GeoDataFrame with one row per region
(``_gdf_*``) and draws one of its columns (``feature``) with ``_plot_choropleth``.

Components are assigned to a region from their bus with ``_region_of``: either the
bus is a region itself (e.g. 'ES0 0AC') or the region is a prefix of the bus name
(e.g. 'ES0 0AC low voltage', 'ES0 0AC battery', 'ES0 0AC urban central heat').
"""

import pandas as pd

from .energy import snapshot_hours
from .filter_columns import filter_df_columns


#################### Common helpers

def _region_of(buses: pd.Series, regions) -> pd.Series:
    """Region of each bus: the bus itself if it is a region, otherwise the longest
    region name followed by a space at the start of the bus name (NaN if none)."""
    names = sorted(set(regions), key=len, reverse=True)

    def match(bus):
        if bus in names:
            return bus
        return next((r for r in names if bus.startswith(r + " ")), None)

    mapping = {bus: match(bus) for bus in pd.unique(buses.astype(str))}
    return buses.astype(str).map(mapping)


def _regions_with_area(gdf_regions):
    """Regions as a gdf with columns 'region', 'geometry' and 'area' [km2]."""
    gdf = gdf_regions.rename(columns={"name": "region"})[["region", "geometry"]].copy()
    gdf["area"] = gdf.to_crs(3035).area / 1e6
    return gdf


def _merge_regions(gdf_regions, df: pd.DataFrame, how: str = "inner"):
    """Merge per-region values (``df`` indexed by region) into the regions gdf."""
    return _regions_with_area(gdf_regions).merge(
        df, left_on="region", right_index=True, how=how
    )


def _plot_choropleth(gdf, feature, ax, params, params_local, titles: dict, prefix=""):
    """Plot ``feature`` of ``gdf`` and set the title from ``titles``.

    ``titles`` maps feature -> (text, unit, show_total). The title reads
    '<prefix><text>. Total: <sum> <unit>' or '<prefix><text> [<unit>]'.
    """
    titles = {"area": ("Area", "km2", True), **titles}
    if feature not in titles:
        raise ValueError(f"feature must be one of {list(titles)}, got {feature!r}")

    vmin = params_local.get("vmin")
    vmax = params_local.get("vmax")
    if vmin in (None, ""):
        vmin = gdf[feature].min()
    if vmax in (None, ""):
        vmax = gdf[feature].max()

    gdf.plot(ax=ax, column=feature,
             cmap=params["cmap"], edgecolor=params["edgecolor"], lw=params["lw"],
             vmin=vmin, vmax=vmax, legend=True)

    text, unit, show_total = titles[feature]
    if feature == "area":
        prefix = ""
    if show_total:
        ax.set_title(f"{prefix}{text}. Total: {gdf[feature].sum():.2f} {unit}")
    else:
        ax.set_title(f"{prefix}{text} [{unit}]")
    return gdf


def _generators_of(n, carrier: str, resource_class) -> pd.DataFrame:
    """Generators of ``carrier`` with their 'region', filtered by ``resource_class``.

    Solar and wind generators are named "<region> <class> <carrier>": with
    ``resource_class`` = <int> only that class is kept, with 'all' every class.
    Other carriers have no classes and ``resource_class`` is ignored.
    """
    gg = n.generators.loc[n.generators["carrier"] == carrier].copy()
    if "wind" in carrier or "solar" in carrier:
        gg["resource_class"] = (
            gg.index.to_series().str[: -(len(carrier) + 1)].str.rsplit(" ", n=1).str[1]
        )
        if isinstance(resource_class, int):
            gg = gg[gg["resource_class"] == str(resource_class)]
        elif resource_class != "all":
            raise ValueError(f"resource_class must be an int or 'all', got {resource_class!r}")
    return gg


#################### Generators

def _gdf_generators(carrier, n, gdf_regions, resource_class):
    gg = _generators_of(n, carrier, resource_class)
    gg["region"] = _region_of(gg["bus"], gdf_regions["name"])
    df = gg.groupby("region")[["p_nom", "p_nom_max", "p_nom_opt"]].sum()

    gdf = _merge_regions(gdf_regions, df)
    for col in ["p_nom", "p_nom_max", "p_nom_opt"]:
        gdf[f"{col}_density"] = gdf[col] / gdf["area"]
    gdf["p_nom_max_ratio"] = gdf["p_nom"] / gdf["p_nom_max"]
    gdf["p_nom_opt_max_ratio"] = gdf["p_nom_opt"] / gdf["p_nom_max"]
    return gdf


def map_network_generators(carrier, n, feature, ax, gdf_regions, resource_class,
                           params, params_local, units="MW"):
    """Map a generation feature of ``carrier`` per region.

    Features:
      - area
      - p_nom               : installed capacity [units]
      - p_nom_density       : p_nom / area [units/km2]
      - p_nom_max           : potential according to land availability [units]
      - p_nom_max_density   : p_nom_max / area [units/km2]
      - p_nom_max_ratio     : p_nom / p_nom_max [-]
      - p_nom_opt           : optimal capacity [units]
      - p_nom_opt_density   : p_nom_opt / area [units/km2]
      - p_nom_opt_max_ratio : p_nom_opt / p_nom_max [-]

    ``units`` = MW | GW | TW applies to capacities and densities (and to vmin/vmax
    in params_local).
    """
    factors = {"MW": 1, "GW": 1e3, "TW": 1e6}
    if units not in factors:
        raise ValueError(f"units must be one of {list(factors)}, got {units!r}")

    gdf = _gdf_generators(carrier, n, gdf_regions, resource_class)
    scaled = ["p_nom", "p_nom_density", "p_nom_max", "p_nom_max_density",
              "p_nom_opt", "p_nom_opt_density"]
    gdf[scaled] = gdf[scaled] / factors[units]

    titles = {
        "p_nom": ("Installed capacity", units, True),
        "p_nom_density": ("Installed capacity density", f"{units}/km2", False),
        "p_nom_max": ("Potential", units, True),
        "p_nom_max_density": ("Potential density", f"{units}/km2", False),
        "p_nom_max_ratio": ("Ratio installed capacity / potential", "-", False),
        "p_nom_opt": ("Optimal capacity", units, True),
        "p_nom_opt_density": ("Optimal capacity density", f"{units}/km2", False),
        "p_nom_opt_max_ratio": ("Ratio optimal capacity / potential", "-", False),
    }
    return _plot_choropleth(gdf, feature, ax, params, params_local, titles,
                            prefix=f"{carrier} : ")


def _gdf_generatorst_pmaxpu(carrier, n, gdf_regions, resource_class):
    if resource_class == "all" and ("wind" in carrier or "solar" in carrier):
        raise ValueError("resource_class='all' is not valid for CF: choose a class number.")
    gg = _generators_of(n, carrier, resource_class)
    gg["region"] = _region_of(gg["bus"], gdf_regions["name"])

    # Weight by snapshot duration [h] so the mean is correct for any temporal resolution
    hours = snapshot_hours(n)
    ts = n.generators_t["p_max_pu"].reindex(columns=gg.index)
    gg["CF"] = ts.multiply(hours, axis=0).sum() / hours.sum()

    return _merge_regions(gdf_regions, gg.groupby("region")[["CF"]].mean())


def map_network_generatorst_pmaxpu(carrier, n, feature, ax, gdf_regions,
                                   params, params_local, gen_class=0):
    """Map the available capacity factor (mean of p_max_pu) of ``carrier`` per region.

    Features:
      - area
      - CF : annual capacity factor [-] of resource class ``gen_class``
    """
    gdf = _gdf_generatorst_pmaxpu(carrier, n, gdf_regions, gen_class)
    titles = {"CF": ("CF", "-", False)}
    return _plot_choropleth(gdf, feature, ax, params, params_local, titles,
                            prefix=f"{carrier} : ")


def _gdf_generatorst_p(carrier, n, gdf_regions, resource_class):
    gg = _generators_of(n, carrier, resource_class)
    gg["region"] = _region_of(gg["bus"], gdf_regions["name"])

    # energy supplied by each generator, weighted by snapshot duration
    supply = n.statistics.supply(components="Generator", groupby=False, nice_names=False)
    gg["AEP"] = supply.reindex(gg.index).fillna(0.0) / 1e6   # TWh

    return _merge_regions(gdf_regions, gg.groupby("region")[["AEP"]].sum())


def map_network_generatorst_p(carrier, n, feature, ax, gdf_regions, resource_class,
                              params, params_local):
    """Map the energy produced by ``carrier`` (dispatch, solved network) per region.

    Features:
      - area
      - AEP : annual energy production [TWh]
    """
    gdf = _gdf_generatorst_p(carrier, n, gdf_regions, resource_class)
    titles = {"AEP": ("Annual Energy Production", "TWh", True)}
    return _plot_choropleth(gdf, feature, ax, params, params_local, titles,
                            prefix=f"{carrier} : ")


#################### Links

# Links whose output (bus1) is electricity: their electric capacity is p_nom * efficiency
_LINKS_ELECTRIC_OUTPUT = ["CCGT", "OCGT", "H2 Fuel Cell", "H2 fuel cell",
                          "battery discharger", "H2 turbine"]


def _gdf_links(carrier, n, gdf_regions):
    lk = n.links.loc[n.links["carrier"] == carrier].copy()
    # region of the link: from bus0, or from bus1 when bus0 is outside the regions
    lk["region"] = _region_of(lk["bus0"], gdf_regions["name"]).fillna(
        _region_of(lk["bus1"], gdf_regions["name"])
    )
    factor = lk["efficiency"] if carrier in _LINKS_ELECTRIC_OUTPUT else 1
    lk["p_nom_e"] = lk["p_nom"] * factor
    lk["p_nom_e_opt"] = lk["p_nom_opt"] * factor

    return _merge_regions(gdf_regions, lk.groupby("region")[["p_nom_e", "p_nom_e_opt"]].sum())


def map_network_links(carrier, n, feature, ax, gdf_regions, params, params_local):
    """Map the capacity of the links of ``carrier`` per region.

    Features:
      - area
      - p_nom_e     : installed capacity [MW] (x efficiency for links producing electricity)
      - p_nom_e_opt : optimal capacity [MW] (x efficiency for links producing electricity)
    """
    gdf = _gdf_links(carrier, n, gdf_regions)
    titles = {
        "p_nom_e": ("Installed capacity", "MW", True),
        "p_nom_e_opt": ("Optimal capacity", "MW", True),
    }
    return _plot_choropleth(gdf, feature, ax, params, params_local, titles,
                            prefix=f"{carrier} : ")


#################### Loads

def _gdf_loadst_pset(n, gdf_regions, load_patterns=None, load_key=None):
    # Select load columns by key or explicit patterns
    cols = filter_df_columns(n.loads_t["p_set"], filter_key=load_key,
                             patterns=load_patterns).columns
    cols = [c for c in cols if c in n.loads.index]

    # Weight by snapshot duration [h] so energy is correct for any temporal resolution
    energy = n.loads_t["p_set"][cols].multiply(snapshot_hours(n), axis=0).sum()
    df = energy.to_frame("annual_load") / 1e6   # TWh
    df["region"] = _region_of(n.loads.loc[cols, "bus"], gdf_regions["name"])

    gdf = _merge_regions(gdf_regions, df.groupby("region")[["annual_load"]].sum(), how="left")
    gdf["annual_load"] = gdf["annual_load"].fillna(0)
    gdf["annual_load_density"] = gdf["annual_load"] / gdf["area"] * 1e3   # GWh/km2
    return gdf


def map_network_loadst_pset(n, feature, ax, gdf_regions, params, params_local,
                            load_patterns=None, load_key=None):
    """Map the annual load per region (time-varying loads, n.loads_t['p_set']).

    Loads are selected with ``load_key`` (e.g. 'electricity', 'heating') or an explicit
    list of ``load_patterns`` (see filter_df_columns); all loads if both are None.

    Features:
      - area
      - annual_load         : [TWh]
      - annual_load_density : [GWh/km2]
    """
    gdf = _gdf_loadst_pset(n, gdf_regions, load_patterns=load_patterns, load_key=load_key)
    titles = {
        "annual_load": ("Annual load", "TWh", True),
        "annual_load_density": ("Annual load density", "GWh/km2", False),
    }
    return _plot_choropleth(gdf, feature, ax, params, params_local, titles)


#################### Storage units and stores

def _gdf_storage_units(carrier, n, gdf_regions):
    su = n.storage_units.loc[n.storage_units["carrier"] == carrier].copy()
    su["region"] = _region_of(su["bus"], gdf_regions["name"])
    su["energy"] = su["p_nom"] * su["max_hours"]
    df = su.groupby("region")[["p_nom", "p_nom_opt", "energy"]].sum()
    # max_hours of the aggregated units: total energy / total power
    df["max_hours"] = df["energy"] / df["p_nom"]

    gdf = _merge_regions(gdf_regions, df.drop(columns="energy"))
    gdf["p_nom_density"] = gdf["p_nom"] / gdf["area"]
    gdf["p_nom_opt_density"] = gdf["p_nom_opt"] / gdf["area"]
    return gdf


def map_network_storage_units(carrier, n, feature, ax, gdf_regions, params, params_local):
    """Map a feature of the storage units of ``carrier`` per region.

    Features:
      - area
      - p_nom             : installed capacity [MW]
      - p_nom_density     : p_nom / area [MW/km2]
      - p_nom_opt         : optimal capacity [MW]
      - p_nom_opt_density : p_nom_opt / area [MW/km2]
      - max_hours         : energy capacity / power capacity [h]
    """
    gdf = _gdf_storage_units(carrier, n, gdf_regions)
    titles = {
        "p_nom": ("Installed capacity", "MW", True),
        "p_nom_density": ("Installed capacity density", "MW/km2", False),
        "p_nom_opt": ("Optimal capacity", "MW", True),
        "p_nom_opt_density": ("Optimal capacity density", "MW/km2", False),
        "max_hours": ("Maximum hours (storage/capacity)", "h", False),
    }
    return _plot_choropleth(gdf, feature, ax, params, params_local, titles,
                            prefix=f"{carrier} : ")


def _gdf_stores(carrier, n, gdf_regions):
    st = n.stores.loc[n.stores["carrier"] == carrier].copy()
    st["region"] = _region_of(st["bus"], gdf_regions["name"])
    df = st.groupby("region")[["e_nom", "e_nom_opt"]].sum() / 1e3   # GWh
    return _merge_regions(gdf_regions, df)


def map_network_stores(carrier, n, feature, ax, gdf_regions, params, params_local):
    """Map the energy capacity of the stores of ``carrier`` per region.

    Features:
      - area
      - e_nom     : installed energy capacity [GWh]
      - e_nom_opt : optimal energy capacity [GWh]
    """
    gdf = _gdf_stores(carrier, n, gdf_regions)
    titles = {
        "e_nom": ("Installed energy storage", "GWh", True),
        "e_nom_opt": ("Optimal energy storage", "GWh", True),
    }
    return _plot_choropleth(gdf, feature, ax, params, params_local, titles,
                            prefix=f"{carrier} : ")
