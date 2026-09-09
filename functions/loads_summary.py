

"""Aggregated annual load summary: sectors (rows) x energy carriers (columns).

The names of the PyPSA loads/carriers (e.g. ``kerosene for aviation``) do not match
the vocabulary used for a high-level demand table (sector ``aviation``, carrier
``oil``), so the translation is done here through an explicit dictionary,
:data:`LOAD_CARRIER_MAP`, which can be extended by the user.

Anything not present in the dictionary is not silently dropped: it is grouped into
``other sectors`` / ``other carriers`` and its name is printed, so it can be added
to the dictionary manually.
"""

from typing import Iterable, Mapping, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

from .energy import snapshot_hours


##### Row (sector) and column (carrier) vocabulary of the summary table.
##### The order here is the order used in the table and in the plot.
SECTOR_ORDER = [
    "electricity",
    "heating",
    "transport",
    "aviation",
    "shipping",
    "industry",
    "agriculture",
    "interconnections",
    "other sectors",
]

CARRIER_ORDER = [
    "electricity",
    "heat",
    "H2",
    "gas",
    "oil",
    "methanol",
    "ammonia",
    "biomass",
    "coal",
    "other carriers",
]

OTHER_SECTOR = "other sectors"
OTHER_CARRIER = "other carriers"


##### Translation of each PyPSA load carrier (``n.loads.carrier``) into the
##### (sector, carrier) pair of the summary table. Extend as needed: any load
##### carrier missing here is reported on screen and grouped into the 'other' buckets.
LOAD_CARRIER_MAP = {
    ### Electricity
    "electricity": ("electricity", "electricity"),
    "industry electricity": ("industry", "electricity"),
    "agriculture electricity": ("agriculture", "electricity"),
    "agriculture machinery electric": ("agriculture", "electricity"),
    "land transport EV": ("transport", "electricity"),
    ### Heat
    "rural heat": ("heating", "heat"),
    "urban central heat": ("heating", "heat"),
    "urban decentral heat": ("heating", "heat"),
    "agriculture heat": ("agriculture", "heat"),
    "low-temperature heat for industry": ("industry", "heat"),
    ### Hydrogen
    "H2 for industry": ("industry", "H2"),
    "H2": ("industry", "H2"),                 # PyPSA-Spain 'H2 valley' demands
    ### Gas
    "gas for industry": ("industry", "gas"),
    ### Oil and derivatives
    "land transport oil": ("transport", "oil"),
    "kerosene for aviation": ("aviation", "oil"),
    "shipping oil": ("shipping", "oil"),
    "naphtha for industry": ("industry", "oil"),
    "agriculture machinery oil": ("agriculture", "oil"),
    ### Methanol
    "shipping methanol": ("shipping", "methanol"),
    "industry methanol": ("industry", "methanol"),
    ### Ammonia
    "NH3": ("industry", "ammonia"),
    ### Biomass
    "solid biomass for industry": ("industry", "biomass"),
    ### Coal
    "coal for industry": ("industry", "coal"),
    ### Interconnections (PyPSA-Spain export loads)
    "electricity_ic": ("interconnections", "electricity"),
    "H2_ic": ("interconnections", "H2"),
}


##### Extra load carriers to drop by hand. Non-energy demands (e.g. 'process emissions',
##### in t_co2) are already detected from the unit declared by their bus, so this list is
##### only an escape hatch for case-by-case exclusions.
LOAD_CARRIER_EXCLUDE = ()


##### Energy units declared by the buses (``n.buses.unit``) and the short quality tag
##### used in the column labels. Everything is MWh, but of a different quality
##### (electric / thermal / lower heating value), so the tag must stay visible.
ENERGY_UNITS = {
    "MWh_el": "el",
    "MWh_th": "th",
    "MWh_LHV": "LHV",
}

##### Buses whose ``unit`` is missing or non-standard upstream, although the quantity
##### they carry is a well-known energy. Keyed by **bus carrier**.
BUS_UNIT_OVERRIDES = {
    # p_set is the fuel input (oil demand / ICE efficiency), i.e. MWh_LHV of oil.
    # PyPSA-Eur labels this bus unit as 'land transport'.
    "land transport oil": "MWh_LHV",
    # The ammonia bus declares no unit upstream.
    "NH3": "MWh_LHV",
}

##### Unit prefix of non-energy quantities (CO2 flows in t/h), excluded from the table.
NON_ENERGY_UNIT_PREFIX = "t_"

UNKNOWN_UNIT_TAG = "?"


##### Colour of each summary carrier (columns), following the PyPSA-Eur palette.
CARRIER_COLORS = {
    "electricity": "#110d63",
    "heat": "#d15959",
    "H2": "#bf13a0",
    "gas": "#e05b09",
    "oil": "#7f7f7f",
    "methanol": "#FF7B00",
    "ammonia": "#46caf0",
    "biomass": "#baa741",
    "coal": "#545454",
    "other carriers": "#b3b3b3",
}


def classify_loads(
    n,
    mapping: Optional[Mapping[str, Sequence[str]]] = None,
    exclude: Optional[Iterable[str]] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Assign a (sector, carrier) pair of the summary table to every load.

    The unit of each load is taken from the bus it is attached to (``n.buses.unit``,
    corrected by :data:`BUS_UNIT_OVERRIDES`). Loads measured in a non-energy unit
    (CO2 flows) are dropped, and loads with an unknown unit are kept but tagged with
    ``'?'`` so they are never lost silently.

    Parameters
    ----------
    n : pypsa.Network
    mapping : dict, optional
        ``{load carrier: (sector, carrier)}``. Defaults to :data:`LOAD_CARRIER_MAP`.
    exclude : iterable, optional
        Extra load carriers to drop by hand. Defaults to :data:`LOAD_CARRIER_EXCLUDE`.
    verbose : bool, default True
        Print the load carriers missing from ``mapping`` and any unit problem, so they
        can be fixed manually.

    Returns
    -------
    DataFrame indexed by load name with columns ``load_carrier``, ``sector``,
    ``carrier``, ``bus_unit``, ``unit_tag``.
    """
    mapping = dict(LOAD_CARRIER_MAP if mapping is None else mapping)
    exclude = set(LOAD_CARRIER_EXCLUDE if exclude is None else exclude)

    load_carrier = (
        n.loads["carrier"] if "carrier" in n.loads else pd.Series("", index=n.loads.index)
    )
    load_carrier = load_carrier.fillna("")

    ### Unit declared by the bus of each load, corrected where it is missing/wrong
    bus_carrier = n.buses["carrier"].reindex(n.loads["bus"]).to_numpy()
    bus_unit = (
        n.buses["unit"].reindex(n.loads["bus"]).to_numpy()
        if "unit" in n.buses
        else np.full(len(n.loads), "")
    )
    bus_unit = pd.Series(bus_unit, index=n.loads.index).fillna("")
    overrides = pd.Series(bus_carrier, index=n.loads.index).map(BUS_UNIT_OVERRIDES)
    bus_unit = overrides.fillna(bus_unit)

    df = pd.DataFrame({"load_carrier": load_carrier, "bus_unit": bus_unit})
    df["unit_tag"] = df["bus_unit"].map(ENERGY_UNITS).fillna(UNKNOWN_UNIT_TAG)

    ### Non-energy loads (t_co2) and manual exclusions never enter an energy table
    non_energy = df["bus_unit"].str.startswith(NON_ENERGY_UNIT_PREFIX)
    dropped = df[non_energy | df["load_carrier"].isin(exclude)]
    df = df.drop(index=dropped.index)

    pairs = df["load_carrier"].map(lambda c: mapping.get(c, (OTHER_SECTOR, OTHER_CARRIER)))
    df["sector"] = [p[0] for p in pairs]
    df["carrier"] = [p[1] for p in pairs]

    if verbose:
        unmapped = sorted(set(df.loc[df["sector"] == OTHER_SECTOR, "load_carrier"]))
        if unmapped:
            print(
                f"⚠  {len(unmapped)} load carrier(s) not in the mapping "
                f"→ grouped into '{OTHER_SECTOR}' / '{OTHER_CARRIER}'. "
                "Add them to functions/loads_summary.py::LOAD_CARRIER_MAP:"
            )
            for name in unmapped:
                print(f"    '{name}': ('<sector>', '<carrier>'),")
        else:
            print("✔  All load carriers are classified.")

        if not dropped.empty:
            info = sorted({f"{c} [{u}]" for c, u in zip(dropped["load_carrier"], dropped["bus_unit"])})
            print(f"ℹ  Excluded, not an energy demand: {', '.join(info)}")

        unknown = df[df["unit_tag"] == UNKNOWN_UNIT_TAG]
        if not unknown.empty:
            info = sorted({f"{c} [{u or 'no unit'}]" for c, u in zip(unknown["load_carrier"], unknown["bus_unit"])})
            print(
                f"⚠  Unknown bus unit, kept but tagged '{UNKNOWN_UNIT_TAG}': {', '.join(info)}. "
                "Map it in functions/loads_summary.py::BUS_UNIT_OVERRIDES."
            )

    return df


def summary_loads_matrix(
    n,
    mapping: Optional[Mapping[str, Sequence[str]]] = None,
    exclude: Optional[Iterable[str]] = None,
    unit: str = "TWh",
    drop_empty: bool = True,
    verbose: bool = True,
) -> pd.DataFrame:
    """Annual aggregated load per sector (rows) and energy carrier (columns).

    ``get_switchable_as_dense`` is used so that **static** loads are included as well:
    most sector demands are constant and therefore absent from ``n.loads_t['p_set']``.
    The resulting power [MW] is weighted by ``n.snapshot_weightings`` (via
    :func:`~functions.energy.snapshot_hours`) to obtain energy, which is correct at any
    temporal resolution. Unlike ``n.statistics.withdrawal``, this works on unsolved
    networks too, where ``n.loads_t['p']`` does not exist yet.

    Parameters
    ----------
    unit : {'TWh', 'GWh', 'MWh'}, default 'TWh'
    drop_empty : bool, default True
        Drop rows/columns whose total is zero.

    Returns
    -------
    DataFrame of annual demand, sectors x carriers.
    """
    scale = {"MWh": 1.0, "GWh": 1e3, "TWh": 1e6}
    if unit not in scale:
        raise ValueError(f"Unknown unit '{unit}'. Use one of {list(scale)}.")

    classes = classify_loads(n, mapping=mapping, exclude=exclude, verbose=verbose)

    ### Dense p_set [MW] for every load (time-varying and static ones)
    p_set = n.get_switchable_as_dense("Load", "p_set")
    hours = snapshot_hours(n)
    energy = p_set.multiply(hours, axis=0).sum() / scale[unit]
    energy = energy.reindex(classes.index).fillna(0.0)

    matrix = (
        pd.DataFrame(
            {
                "sector": classes["sector"],
                "carrier": classes["carrier"],
                "value": energy,
            }
        )
        .groupby(["sector", "carrier"])["value"]
        .sum()
        .unstack("carrier")
        .fillna(0.0)
    )

    ### Apply the reference ordering, keeping any unexpected label at the end
    rows = [s for s in SECTOR_ORDER if s in matrix.index]
    rows += [s for s in matrix.index if s not in rows]
    cols = [c for c in CARRIER_ORDER if c in matrix.columns]
    cols += [c for c in matrix.columns if c not in cols]
    matrix = matrix.loc[rows, cols]

    if drop_empty:
        matrix = matrix.loc[matrix.sum(axis=1) != 0, matrix.sum(axis=0) != 0]

    matrix.index.name = "sector"
    matrix.columns.name = "carrier"

    ### Unit of each column, from the buses of the loads that actually contribute to it.
    ### Stored in `attrs` so the plot can label the columns; a column mixing qualities
    ### (should not happen) shows all of them, e.g. 'TWh_LHV+th'.
    contributing = classes.loc[energy[energy != 0].index.intersection(classes.index)]
    units = {}
    for carrier in matrix.columns:
        tags = sorted(set(contributing.loc[contributing["carrier"] == carrier, "unit_tag"]))
        units[carrier] = f"{unit}_{'+'.join(tags)}" if tags else unit
    matrix.attrs["units"] = units
    matrix.attrs["unit"] = unit

    if verbose:
        print("ℹ  Column units (from n.buses.unit): " + ", ".join(f"{c}: {u}" for c, u in units.items()))

    return matrix


def plot_loads_matrix(
    matrix: pd.DataFrame,
    unit: Optional[str] = None,
    units: Optional[Mapping[str, str]] = None,
    colors: Optional[Mapping[str, str]] = None,
    max_side: float = 0.86,
    label_threshold: float = 0.02,
    fmt: str = "{:.1f}",
    ax=None,
    figsize=None,
):
    """Matrix of squares whose **area** is the annual demand of each (sector, carrier).

    The colour encodes the **carrier** (column), not the sector, so each column shares
    one colour and the squares can be compared across sectors at a glance.

    Parameters
    ----------
    matrix : DataFrame
        Output of :func:`summary_loads_matrix` (sectors x carriers).
    unit, units : optional
        Base unit and per-column unit (e.g. ``{'oil': 'TWh_LHV'}``). Both default to the
        values stored in ``matrix.attrs`` by :func:`summary_loads_matrix`.
    max_side : float, default 0.86
        Side of the largest square, in cell units (1 = full cell).
    label_threshold : float, default 0.02
        Values below this fraction of the maximum are not annotated.
    """
    unit = unit or matrix.attrs.get("unit", "TWh")
    units = units if units is not None else matrix.attrs.get("units", {})
    colors = dict(CARRIER_COLORS if colors is None else colors)
    values = matrix.clip(lower=0)
    vmax = values.to_numpy().max()
    if vmax <= 0:
        raise ValueError("The load matrix has no positive values to plot.")

    n_rows, n_cols = matrix.shape
    if figsize is None:
        figsize = (1.05 * n_cols + 3.0, 0.95 * n_rows + 2.0)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    for i, sector in enumerate(matrix.index):
        for j, carrier in enumerate(matrix.columns):
            value = values.iat[i, j]
            if value <= 0:
                continue
            ### Area proportional to the demand -> side proportional to its square root
            side = max_side * np.sqrt(value / vmax)
            ax.add_patch(
                Rectangle(
                    (j - side / 2, i - side / 2),
                    side,
                    side,
                    facecolor=colors.get(carrier, "#b3b3b3"),
                    edgecolor="none",
                    alpha=0.9,
                )
            )
            if value / vmax >= label_threshold:
                ### Label inside the square when it fits, above it otherwise
                inside = side > 0.34
                ax.text(
                    j,
                    i if inside else i - side / 2 - 0.14,
                    fmt.format(value),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if inside else "0.25",
                )

    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(n_rows - 0.5, -0.5)          # first sector on top
    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))
    ### Each column carries its own unit: electricity is MWh_el, heat MWh_th and the
    ### fuels MWh_LHV, so the quality of the energy must stay visible on the label.
    ax.set_xticklabels(
        [f"{c}\n[{units.get(c, unit)}]" for c in matrix.columns], rotation=45, ha="left"
    )
    ax.set_yticklabels(matrix.index)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.set_ylabel("sector")
    ax.set_aspect("equal")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, n_cols + 0.5, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows + 0.5, 1), minor=True)
    ax.grid(True, which="minor", linestyle="--", alpha=0.3)

    total = values.to_numpy().sum()
    ### The total adds up energies of different quality (el / th / LHV), i.e. it is a
    ### final-energy figure, not a primary-energy one: say so instead of hiding it.
    qualities = sorted({units.get(c, unit) for c in matrix.columns})
    mixed = ", mixed " + "/".join(q.split("_", 1)[-1] for q in qualities) if len(qualities) > 1 else ""
    ax.set_title(
        f"Annual load "
        f"(largest: {fmt.format(vmax)} {unit}; total: {fmt.format(total)} {unit}{mixed})",
        pad=34,
    )
    return ax
