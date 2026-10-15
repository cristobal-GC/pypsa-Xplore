"""Summaries of the generators of a network: capacity per carrier, capacity and
capacity factor / energy per bus and resource class, and capital cost distribution."""

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .energy import snapshot_hours


def summary_generators_by_carrier(n, units: str = "MW") -> pd.DataFrame:
    """Aggregated, potential and optimal capacity per generator carrier, in ``units``
    (MW | GW | TW).

    p_nom is assumed to be in MW (PyPSA convention). p_nom_opt is only filled once the
    network is solved (zero before). Returns a styled table with two decimals, sorted
    by optimal capacity (descending).
    """
    factors = {"MW": 1, "GW": 1e3, "TW": 1e6}
    if units not in factors:
        raise ValueError(f"units must be one of {list(factors)}, got {units!r}")
    df = n.generators.groupby("carrier").agg(
        Total_capacity=pd.NamedAgg(column="p_nom", aggfunc="sum"),
        Total_max_capacity=pd.NamedAgg(column="p_nom_max", aggfunc="sum"),
        Total_opt_capacity=pd.NamedAgg(column="p_nom_opt", aggfunc="sum"),
    ) / factors[units]
    df = df.sort_values("Total_opt_capacity", ascending=False)
    return df.style.set_caption(f"Capacity [{units}] per carrier.").format("{:.2f}")


def _generators_by_resource_class(n, carrier: str) -> pd.DataFrame:
    """Generators of ``carrier`` with the region in 'bus' and an extra 'resource_class'.

    Generator names are "<region> <class> <carrier>". Both are parsed from the name
    once the carrier suffix is removed, so carriers with spaces (e.g. 'solar rooftop')
    and generators attached to another bus of the region (e.g. '<region> low voltage')
    are handled too.
    """
    gg = n.generators.loc[n.generators["carrier"] == carrier].copy()
    prefix = gg.index.to_series().str[: -(len(carrier) + 1)].str.rsplit(" ", n=1)
    gg["bus"] = prefix.str[0]
    gg["resource_class"] = prefix.str[1]
    return gg


def _bars_by_bus_and_class(df: pd.DataFrame, colors: dict, ylabel: str, width: float):
    """Grouped bar plot: one group per bus, one bar per resource class; for each
    class, one bar per column in ``colors`` (drawn in that order, overlapping)."""
    df_sorted = df.sort_values(["bus", "resource_class"])
    buses = df_sorted["bus"].unique()
    resources = df_sorted["resource_class"].unique()
    x = np.arange(len(buses))
    offsets = np.linspace(-width / 2.5, width / 2.5, len(resources))

    fig, ax = plt.subplots(figsize=(12, 8))
    labels_added = set()
    for i, res in enumerate(resources):
        df_res = df_sorted[df_sorted["resource_class"] == res].set_index("bus").reindex(buses)
        for metric, color in colors.items():
            label = metric if metric not in labels_added else None
            ax.bar(x + offsets[i], df_res[metric], width=width / len(resources),
                   color=color, alpha=0.7, label=label)
            labels_added.add(metric)
    ax.set_xticks(x)
    ax.set_xticklabels(buses, fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.set_xlabel("Bus", fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.tick_params(axis="y", labelsize=14)
    ax.legend(fontsize=14)
    plt.tight_layout()
    return ax


def summary_generators_by_resource_class(
    n,
    carrier: str,
    feature: str = "p_nom",
    units: str = "GW",
    width: float = 0.3,
):
    """Capacities of a solar/wind ``carrier`` per bus and resource class, in ``units``
    (MW | GW | TW).

    Draws a bar plot with p_nom_max, p_nom_opt and p_nom per bus and class, and returns
    a styled table of ``feature`` (p_nom | p_nom_max | p_nom_opt) by bus (rows) and
    class (columns). p_nom_opt is only filled once the network is solved (zero before).
    Returns None if the carrier has no resource classes.
    """
    factors = {"MW": 1, "GW": 1e3, "TW": 1e6}
    if units not in factors:
        raise ValueError(f"units must be one of {list(factors)}, got {units!r}")
    metrics = ["p_nom", "p_nom_max", "p_nom_opt"]
    if feature not in metrics:
        raise ValueError(f"feature must be one of {metrics}, got {feature!r}")
    if not ("wind" in carrier or "solar" in carrier):
        print(f"Carrier {carrier} is not solar or wind type.. does it contain classes?")
        return None

    gg = _generators_by_resource_class(n, carrier)[["bus", "resource_class"] + metrics]
    gg[metrics] = gg[metrics] / factors[units]

    #################### Bar plot
    _bars_by_bus_and_class(
        gg, {"p_nom_max": "#cfe2f3", "p_nom_opt": "#4daf4a", "p_nom": "#08306b"},
        ylabel=f"Capacity [{units}]", width=width,
    )

    #################### Table
    return (
        gg.pivot(index="bus", columns="resource_class", values=feature)
        .style.set_caption(f"{feature} [{units}] for {carrier}, by bus and class.")
        .format("{:.2f}")
        .background_gradient(cmap="Blues")
    )


def summary_generators_t_by_resource_class(
    n,
    carrier: str,
    feature: str = "CF",
    units: str = "TWh",
    width: float = 0.3,
):
    """Capacity factor or annual energy of a solar/wind ``carrier`` per bus and
    resource class.

    feature:
      - CF  : mean of generators_t['p_max_pu'] (available capacity factor) [-]
      - AEP : energy from the dispatch generators_t['p'] (solved network only), in
              ``units`` (MWh | GWh | TWh)

    Both are weighted by the snapshot duration, so they are correct for any temporal
    resolution. Draws a bar plot and returns a styled table by bus (rows) and class
    (columns). Returns None if the carrier has no resource classes.
    """
    factors = {"MWh": 1, "GWh": 1e3, "TWh": 1e6}
    if units not in factors:
        raise ValueError(f"units must be one of {list(factors)}, got {units!r}")
    if feature not in ("CF", "AEP"):
        raise ValueError(f"feature must be 'CF' or 'AEP', got {feature!r}")
    if not ("wind" in carrier or "solar" in carrier):
        print(f"Carrier {carrier} is not solar or wind type.. does it contain classes?")
        return None

    gg = _generators_by_resource_class(n, carrier)[["bus", "resource_class"]]
    hours = snapshot_hours(n)
    if feature == "CF":
        ts = n.generators_t["p_max_pu"].reindex(columns=gg.index)
        gg["CF"] = ts.multiply(hours, axis=0).sum() / hours.sum()
        color, ylabel, caption = "#bc91d8", "CF", f"CF for {carrier}"
    else:
        ts = n.generators_t["p"].reindex(columns=gg.index)
        gg["AEP"] = ts.multiply(hours, axis=0).sum() / factors[units]
        color, ylabel, caption = "#93c543", f"AEP [{units}]", f"AEP [{units}] for {carrier}"

    #################### Bar plot
    _bars_by_bus_and_class(gg, {feature: color}, ylabel=ylabel, width=width)

    #################### Table
    return (
        gg.pivot(index="bus", columns="resource_class", values=feature)
        .style.set_caption(f"{caption}, by bus and class.")
        .format("{:.3f}")
        .background_gradient(cmap="Blues")
    )


def plot_generators_capital_cost(n, carrier_list: Sequence[str], bins: int = 20):
    """Distribution of the generators' capital cost [EUR/(MW·year)] for ``carrier_list``.

    Carriers with a single value (e.g. onwind, solar) are drawn as vertical lines;
    carriers whose cost varies between generators (e.g. offshore, through the grid
    connection cost) as a histogram of ``bins`` bins spanning their own range.

    capital_cost is annualised and multiplied by the modelled fraction of a year
    (nyears = sum of snapshot weightings / 8760), so it is divided by nyears here.

    Returns a styled table with the number of generators and the min / mean / max
    capital cost per carrier (unweighted).
    """
    gg = n.generators
    present = [c for c in carrier_list if c in gg["carrier"].unique()]
    if not present:
        print(f"None of the selected carriers is present. Available: "
              f"{sorted(gg['carrier'].unique())}")
        return None

    nyears = n.snapshot_weightings.objective.sum() / 8760.0
    cost = gg.loc[gg["carrier"].isin(present), ["carrier", "capital_cost"]].copy()
    cost["capital_cost"] /= nyears

    fig, ax = plt.subplots(figsize=[10, 5])
    tech_colors = n.carriers["color"]
    for carrier in present:
        values = cost.loc[cost["carrier"] == carrier, "capital_cost"]
        color = tech_colors.get(carrier) or None
        if values.round(2).nunique() == 1:
            ax.axvline(x=values.iloc[0], label=carrier, color=color)
        else:
            ax.hist(values, bins=bins, edgecolor="none", color=color,
                    label=carrier, alpha=0.7)
    ax.set_title("Capital cost of generators")
    ax.set_xlabel("EUR/(MW·year)")
    ax.set_yticklabels([])
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    summary = cost.groupby("carrier")["capital_cost"].agg(["count", "min", "mean", "max"])
    return (
        summary.loc[present]
        .style.set_caption("Capital cost [EUR/(MW·year)] per carrier (unweighted).")
        .format("{:.2f}", subset=["min", "mean", "max"])
    )
