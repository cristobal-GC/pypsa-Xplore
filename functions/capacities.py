import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Bus carriers that hold electricity
ELECTRIC_BUS_CARRIERS = ["AC", "low voltage"]


def _dynamic_efficiency_links(n, units_factor: float) -> pd.DataFrame:
    """Electric capacity of the links with a time-varying efficiency at an electric bus1.

    n.statistics uses the static efficiency, which is only a placeholder for these
    links (e.g. heat pumps in PyPSA-Eur: bus0 = heat, bus1 = low voltage, operated with
    negative power, efficiency = 1/COP varying in time, p_nom in MW of heat).

    Their electric capacity is p_nom x max(efficiency), i.e. the peak electric power at
    bus1, negative when the link is operated in reverse (p_max_pu <= 0: it withdraws
    from bus1) and positive otherwise (it supplies bus1).
    """
    lk = n.links
    dyn = [l for l in n.links_t["efficiency"].columns
           if n.buses["carrier"].get(lk.at[l, "bus1"]) in ELECTRIC_BUS_CARRIERS]
    if not dyn:
        return pd.DataFrame(columns=["Initial_capacity", "Optimal_capacity"])

    peak_eff = n.links_t["efficiency"][dyn].max()
    reversed_ = n.get_switchable_as_dense("Link", "p_max_pu")[dyn].max() <= 0
    factor = peak_eff * np.where(reversed_, -1.0, 1.0) / units_factor

    df = pd.DataFrame({
        "Initial_capacity": lk.loc[dyn, "p_nom"] * factor,
        "Optimal_capacity": lk.loc[dyn, "p_nom_opt"] * factor,
    }).groupby(lk.loc[dyn, "carrier"]).sum()
    df.index = pd.MultiIndex.from_product([["Link"], df.index], names=["component", "carrier"])
    return df


def summary_electric_capacities(n, units: str = "GW"):
    """Initial and optimal electric capacity at the AC and low-voltage buses, per
    component and carrier.

    Uses n.statistics.installed_capacity / optimal_capacity with
    bus_carrier=['AC', 'low voltage']: the capacity of each generator, storage unit and
    link is measured at its port on an electric bus (for a link, p_nom x efficiency of
    that port, so e.g. a CCGT counts its electric output). Sign convention:
      - positive : capacity that supplies the electric buses (generators, CCGT,
                   solar rooftop, battery discharge, V2G, imports)
      - negative : capacity that withdraws from them (electrolysis, battery and BEV
                   charge, heat pumps, exports, pipeline compression)

    Links with a time-varying efficiency (heat pumps) are corrected with
    ``_dynamic_efficiency_links``, since n.statistics uses their static efficiency.
    Links between two electric buses (DC lines, distribution grid) are left out: their
    net value at the electric ports is just losses or flows in opposite directions.

    Draws a horizontal bar plot and returns a styled table in ``units`` (MW | GW | TW),
    sorted by optimal capacity (descending). Rows that are zero at two decimals are
    dropped.
    """
    factors = {"MW": 1, "GW": 1e3, "TW": 1e6}
    if units not in factors:
        raise ValueError(f"units must be one of {list(factors)}, got {units!r}")

    S = n.statistics
    kw = dict(components=["Generator", "Link", "StorageUnit"],
              bus_carrier=ELECTRIC_BUS_CARRIERS, nice_names=False)
    df = pd.concat(
        {"Initial_capacity": S.installed_capacity(**kw),
         "Optimal_capacity": S.optimal_capacity(**kw)},
        axis=1,
    ).fillna(0.0) / factors[units]
    df.index.names = ["component", "carrier"]

    ##### Links with time-varying efficiency (heat pumps): replace their values
    dyn = _dynamic_efficiency_links(n, factors[units])
    if not dyn.empty:
        df = pd.concat([df.drop(dyn.index, errors="ignore"), dyn])

    ##### Leave out links between two electric buses (grid, not capacity)
    lk = n.links
    elec0 = lk["bus0"].map(n.buses["carrier"]).isin(ELECTRIC_BUS_CARRIERS)
    elec1 = lk["bus1"].map(n.buses["carrier"]).isin(ELECTRIC_BUS_CARRIERS)
    grid = lk.loc[elec0 & elec1, "carrier"].unique()
    df = df.drop([("Link", c) for c in grid], errors="ignore")

    # drop rows that are zero at the displayed precision (two decimals)
    df = df.loc[(df.abs() >= 0.005).any(axis=1)].sort_values("Optimal_capacity", ascending=False)

    #################### Bar plot
    title = "Electric capacity at AC and low-voltage buses"
    df_plot = df.droplevel("component").iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 0.35 * len(df_plot) + 1.5))
    df_plot.plot(kind="barh", ax=ax, width=0.8, color={"Initial_capacity": "#9ecae1",
                                                         "Optimal_capacity": "#08306b"})
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel(f"{title} [{units}]  (+ supply / - withdrawal)")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_title(title)
    plt.tight_layout()

    #################### Table
    return (
        df.style.set_caption(f"{title} [{units}] (+ supply / - withdrawal).")
        .format("{:.2f}")
    )
