

from typing import Optional, Sequence

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd

from .map_add_features import map_add_features
from .map_add_region import map_add_region


def plot_network_map(
    n,
    gdf_regions_onshore,
    gdf_regions_offshore,
    params: dict,
    boundaries: Sequence[float],
    line_widths=None,
    link_widths=None,
    figsize=(12, 12),
    ax=None,
):
    """Plot the recurring network map (network + onshore/offshore regions + features).

    ``boundaries`` is a user-provided ``[lon_min, lon_max, lat_min, lat_max]`` list, so
    the map frames any spatial domain (ES, EU, custom country set) without NUTS files.
    """
    if line_widths is None:
        line_widths = 1 * n.lines.s_nom / 1e3
    if link_widths is None:
        link_widths = 1 * n.links.p_nom / 1e3

    if ax is None:
        fig, ax = plt.subplots(
            figsize=figsize, subplot_kw={"projection": ccrs.PlateCarree()}
        )

    ### Add network
    n.plot(
        ax=ax,
        line_widths=line_widths,
        link_widths=link_widths,
        bus_sizes=params["bus_sizes"],
        bus_colors=params["bus_colors"],
        boundaries=boundaries,
    )

    ### Add onshore / offshore regions
    map_add_region(ax, gdf_regions_onshore, params["map_add_region"])
    map_add_region(ax, gdf_regions_offshore, params["map_add_region"], is_offshore=True)

    ### Add map features
    map_add_features(ax, params["map_add_features"])

    return ax


def plot_length_hist(series: pd.Series, bins: int = 50, xlabel: str = "km", figsize=(10, 4)):
    """Histogram of a length series (line / DC-link lengths)."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(series, bins=bins, edgecolor="black")
    ax.set_xlabel(xlabel)
    ax.grid(True, linestyle="--", alpha=0.5)
    return ax


def plot_cost_vs_length(
    df: pd.DataFrame,
    x: str = "length",
    y: str = "capital_cost",
    xlabel: str = "km",
    ylabel: str = "EUR/MW",
    unit: str = "EUR/(MW·km)",
    figsize=(10, 4),
):
    """Scatter of capital cost vs length and print the cost/length ratio values."""
    fig, ax = plt.subplots(figsize=figsize)
    df.plot(ax=ax, kind="scatter", x=x, y=y)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", alpha=0.5)

    ratio = (df[y] / df[x]).round(2).unique()
    print(f"The ratio values of capital cost vs. length are {ratio} {unit}")
    return ax


def summary_generators_by_carrier(n) -> pd.DataFrame:
    """Aggregated and potential capacity per generator carrier [same units as p_nom]."""
    return n.generators.groupby("carrier").agg(
        Total_capacity=pd.NamedAgg(column="p_nom", aggfunc="sum"),
        Total_max_capacity=pd.NamedAgg(column="p_nom_max", aggfunc="sum"),
    )


def notify_skipped(section: str) -> None:
    """Standard notice printed by a guarded section when its data is not available."""
    print(f"⏭  '{section}' not available for this network state.")
