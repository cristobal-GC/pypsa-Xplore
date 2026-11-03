"""Electricity exchanges through the border links of pypsa-spain (carriers 'DC_ic export' /
'DC_ic import'): energy balance, power time series and heatmaps, and the economic result of
the trade with each neighbouring country (solved network)."""

from typing import Sequence

import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .energy import snapshot_hours
from .get_ic_colors import get_ic_colors

IC_CARRIERS = ["DC_ic export", "DC_ic import"]

##### Diverging pink (import, < 0) / green (export, > 0), ends trimmed for softer tones
IC_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "soft_PiYG", plt.cm.PiYG(np.linspace(0.25, 0.75, 256)),
)
IC_SIDE_COLORS = {"export": plt.cm.PiYG(0.75), "import": plt.cm.PiYG(0.25)}


def _ic_balance(n, aggregate_time: bool = True) -> pd.Series | pd.DataFrame:
    """Energy [MWh] (or power [MW] per snapshot, with ``aggregate_time=False``) at the
    Spanish AC port of each border link: + import (injects into the AC bus), - export."""
    return n.statistics.energy_balance(
        components="Link", carrier=IC_CARRIERS, bus_carrier="AC",
        groupby=False, nice_names=False, aggregate_time="sum" if aggregate_time else False,
    )


def _country_trade(n, country: str) -> dict:
    """Prices and flows of the trade with ``country``, per side ('export' | 'import').

    Each border link ends at a border bus with a market generator: 'DC_ic market export'
    (sign = -1, marginal_cost = -(export price)) or 'DC_ic market import' (marginal_cost =
    import price). For each side, returns DataFrames indexed by snapshot with one column
    per border link of the country:
      - market   : power at the border bus, i.e. traded with the market [MW]
      - price    : market price [€/MWh]
      - es       : power at the Spanish AC bus (before the link losses for exports,
                   after them for imports) [MW]
      - price_es : Spanish nodal price at that bus [€/MWh]
    """
    gen = n.generators
    mc = n.get_switchable_as_dense("Generator", "marginal_cost")
    trade = {}
    for side, sign in [("export", -1), ("import", 1)]:
        links = n.links.index[(n.links["carrier"] == f"DC_ic {side}")
                              & n.links.index.str.contains(f" {country}")]
        es_col, border_col = ("bus0", "bus1") if side == "export" else ("bus1", "bus0")
        data = {key: {} for key in ["market", "price", "es", "price_es"]}
        for link in links:
            es_bus, border_bus = n.links.at[link, es_col], n.links.at[link, border_col]
            g = gen.index[(gen["bus"] == border_bus) & (gen["carrier"] == f"DC_ic market {side}")][0]
            data["market"][link] = n.generators_t["p"][g]
            data["price"][link] = sign * mc[g]
            data["es"][link] = n.links_t["p0"][link] if side == "export" else -n.links_t["p1"][link]
            data["price_es"][link] = n.buses_t["marginal_price"][es_bus]
        trade[side] = {key: pd.DataFrame(value) for key, value in data.items()}
    return trade


def plot_interconnections_energy(n, units: str = "TWh"):
    """Stacked bars of the energy imported and exported through each border link, in
    ``units`` (MWh | GWh | TWh), weighted by the snapshot duration."""
    factors = {"MWh": 1, "GWh": 1e3, "TWh": 1e6}
    if units not in factors:
        raise ValueError(f"units must be one of {list(factors)}, got {units!r}")

    balance = _ic_balance(n) / factors[units]
    combined = pd.DataFrame({
        "Imports": balance.clip(lower=0),
        "Exports": -balance.clip(upper=0),
    }).T

    ic_color_dict = get_ic_colors(combined.columns)
    colors = [ic_color_dict[col] for col in combined.columns]

    fig, ax = plt.subplots(figsize=[6, 6])
    combined.plot(kind="bar", stacked=True, color=colors, ax=ax, width=0.7)
    ax.set_ylabel(units)
    ax.set_xlabel("")
    ax.grid(True, linestyle="--", linewidth=0.5, color="black", alpha=0.25)
    ax.legend(title="Border links", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    plt.tight_layout()
    return ax


def plot_interconnections_timeseries(n, start: str, end: str):
    """Stacked power [GW] of each border link between ``start`` and ``end``: exports
    positive, imports negative. Power at each snapshot, not weighted."""
    flows = _ic_balance(n, aggregate_time=False).T.loc[start:end] / 1e3
    is_export = n.links.loc[flows.columns, "carrier"] == "DC_ic export"
    exports_plot = -flows.loc[:, is_export]    # positive
    imports_plot = -flows.loc[:, ~is_export]   # negative

    ic_color_dict = get_ic_colors(flows.columns)
    export_colors = [ic_color_dict.get(col, "#808080") for col in exports_plot.columns]
    import_colors = [ic_color_dict.get(col, "#808080") for col in imports_plot.columns]

    fig, ax = plt.subplots(figsize=[10, 4])
    ax.stackplot(exports_plot.index, exports_plot.T.values,
                 labels=[f"{c} (export)" for c in exports_plot.columns],
                 colors=export_colors, alpha=0.85)
    ax.stackplot(imports_plot.index, imports_plot.T.values,
                 labels=[f"{c} (import)" for c in imports_plot.columns],
                 colors=import_colors, alpha=0.45)
    ax.axhline(0, color="black", linewidth=0.8, alpha=0.7)
    ax.set_ylabel("Power [GW]")
    ax.set_xlabel("")
    ax.grid(True, linestyle="--", linewidth=0.5, color="black", alpha=0.25)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False, fontsize=9)
    plt.tight_layout()
    return ax


def plot_interconnections_heatmap(n, countries: Sequence[str] = ("FR", "PT"), tol: float = 1e-3):
    """One heatmap per country of the net exchange [GW] (sum of all its border links):
    days on the x axis, hours on the y axis, + export / - import, colour scale centred at 0.

    The title gives the share of time exporting, importing and at zero (|net| below
    ``tol`` [GW], solver residuals), weighted by the snapshot duration. Snapshots longer
    than one hour are placed at their starting hour.
    """
    flows = -_ic_balance(n, aggregate_time=False).T / 1e3      # + export, - import
    hours = snapshot_hours(n)

    for country in countries:
        ##### Sum of the border links of the country, reshaped to hour (rows) x day (columns)
        net = flows.loc[:, flows.columns.str.contains(f" {country}")].sum(axis=1)
        heat = net.groupby([net.index.hour, net.index.normalize()]).mean().unstack()

        pct_exp = 100 * hours[net > tol].sum() / hours.sum()
        pct_imp = 100 * hours[net < -tol].sum() / hours.sum()
        pct_zero = 100 - pct_exp - pct_imp

        fig, ax = plt.subplots(figsize=[14, 4])
        mesh = ax.pcolormesh(
            heat.columns, heat.index, heat.values, shading="nearest",
            cmap=IC_CMAP, norm=mcolors.CenteredNorm(vcenter=0),
        )
        cbar = fig.colorbar(mesh, ax=ax, pad=0.01)
        cbar.set_label("Power [GW]\n(+ export / - import)")
        ax.set_title(f"Net exchange with {country}: export {pct_exp:.1f}%, "
                     f"import {pct_imp:.1f}%, zero {pct_zero:.1f}%")
        ax.set_ylabel("Hour")
        ax.set_yticks(range(0, 24, 3))
        ax.invert_yaxis()
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        plt.tight_layout()


def summary_interconnections_trade(
    n,
    countries: Sequence[str] = ("FR", "PT"),
    bin_width: float = 10,
    price_cut: float = 0.99,
):
    """Economic balance of the trade with each country: export revenue - import cost.

    Energy is measured at the border bus (after the link losses), as in the objective
    function. Draws, per country, histograms of the energy traded per price bin of
    ``bin_width`` [€/MWh] (dashed lines: energy-weighted average prices), with the x axis
    up to the ``price_cut`` quantile of the traded energy (long price tails). Returns a
    styled table with energy [TWh], average price [€/MWh] and money [M€] per side.
    """
    hours = snapshot_hours(n)
    rows = {}
    for country in countries:
        trade = {}
        for side, data in _country_trade(n, country).items():
            energy = data["market"].multiply(hours, axis=0)              # [MWh] per link
            df = pd.DataFrame({
                "energy": energy.sum(axis=1),                             # [MWh]
                "money": (energy * data["price"]).sum(axis=1),            # [€]
            })
            df["price"] = (df["money"] / df["energy"]).fillna(data["price"].mean(axis=1))
            trade[side] = df

        revenue = trade["export"]["money"].sum() / 1e6     # [M€]
        cost = trade["import"]["money"].sum() / 1e6        # [M€]

        ##### x axis limit: energy-weighted quantile of the prices of both sides
        both = pd.concat(trade.values()).sort_values("price")
        cum = both["energy"].cumsum() / both["energy"].sum()
        x_max = bin_width * np.ceil(both.loc[cum >= price_cut, "price"].iloc[0] / bin_width)
        bins = np.arange(0, both["price"].max() + bin_width, bin_width)

        fig, ax = plt.subplots(figsize=[10, 5])
        notes = []
        row = {}
        for side, df in trade.items():
            e_twh = df["energy"].sum() / 1e6
            avg = df["money"].sum() / df["energy"].sum()
            row.update({(side, "energy [TWh]"): e_twh, (side, "avg price [€/MWh]"): avg,
                        (side, "money [M€]"): df["money"].sum() / 1e6})
            ax.hist(df["price"], bins=bins, weights=df["energy"] / 1e6, color=IC_SIDE_COLORS[side],
                    alpha=0.6, label=f"{side.capitalize()}: {e_twh:.1f} TWh at {avg:.1f} €/MWh (avg)")
            ax.axvline(avg, color=IC_SIDE_COLORS[side], linestyle="--", linewidth=1.5)
            off = 100 * df.loc[df["price"] > x_max, "energy"].sum() / df["energy"].sum()
            if off > 0:
                notes.append(f"{side} {off:.1f}%")
        row[("balance", "money [M€]")] = revenue - cost
        rows[country] = row

        if notes:
            ax.text(0.99, 0.70, f"Energy above {x_max:.0f} €/MWh (off-scale):\n" + ", ".join(notes),
                    transform=ax.transAxes, ha="right", va="top", fontsize=9, color="0.3")
        ax.set_xlim(0, x_max)
        ax.set_xlabel("Price [€/MWh]")
        ax.set_ylabel(f"Energy traded per {bin_width} €/MWh bin [TWh]")
        ax.set_title(f"Trade with {country}: balance {revenue - cost:+.0f} M€ "
                     f"(export revenue {revenue:.0f} M€ - import cost {cost:.0f} M€)")
        ax.grid(True, linestyle="--", linewidth=0.5, color="black", alpha=0.25)
        ax.legend(frameon=False)
        plt.tight_layout()

    #################### Table
    return (
        pd.DataFrame(rows).T
        .style.set_caption("Trade with each country (export revenue - import cost).")
        .format("{:.1f}")
    )


def summary_interconnections_gain(
    n,
    countries: Sequence[str] = ("FR", "PT"),
    price_cut: float = 0.99,
    tol: float = 1,
):
    """Gain from the trade with each country, valuing the exchanged energy at the Spanish
    nodal price of the AC bus each border link is connected to:
      - export: market revenue - value of the energy that leaves Spain at the Spanish price
      - import: value of the energy that reaches Spain at the Spanish price - market cost

    In an optimal dispatch it is only positive when the link is at full capacity (congestion
    rent of the interconnections). Draws, per country, a scatter of the Spanish vs foreign
    price of each traded hour (traded power above ``tol`` [MW]; axes up to the ``price_cut``
    quantile of the prices) and the monthly gain. Returns a styled table of the gain [M€].
    """
    hours = snapshot_hours(n)
    rows = {}
    for country in countries:
        points, gains = {}, {}
        for side, data in _country_trade(n, country).items():
            market = data["market"] * data["price"]        # [€/h] per link
            domestic = data["es"] * data["price_es"]       # [€/h] per link
            gain = (market - domestic) if side == "export" else (domestic - market)
            gains[side] = gain.sum(axis=1) * hours         # [€]
            traded = data["es"] > tol
            points[side] = pd.concat([
                pd.DataFrame({"es": data["price_es"].loc[traded[link], link],
                              "foreign": data["price"].loc[traded[link], link]})
                for link in data["es"].columns
            ])

        monthly = pd.DataFrame(gains).groupby(lambda t: t.month).sum() / 1e6     # [M€]
        total = monthly.sum()
        rows[country] = {**total, "total": total.sum()}

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[14, 5.5], gridspec_kw={"width_ratios": [1, 1.3]})

        ##### Scatter: Spanish vs foreign price of each traded hour
        lim = max(pd.concat(points.values()).quantile(price_cut))
        for side, df in points.items():
            ax1.scatter(df["es"], df["foreign"], s=4, alpha=0.3, color=IC_SIDE_COLORS[side],
                        label=side.capitalize(), rasterized=True)
        ax1.plot([0, lim], [0, lim], color="0.3", linewidth=0.8, linestyle="--")
        ax1.set_xlim(0, lim)
        ax1.set_ylim(0, lim)
        ax1.set_aspect("equal")
        ax1.set_xlabel("Spanish nodal price [€/MWh]")
        ax1.set_ylabel(f"{country} price [€/MWh]")
        ax1.set_title("Prices of each traded hour")
        ax1.legend(frameon=False, markerscale=4, loc="upper left")
        ax1.grid(True, linestyle="--", linewidth=0.5, color="black", alpha=0.25)

        ##### Monthly gain from exports and imports (stacked)
        monthly.columns = [f"{side.capitalize()}: {total[side]:+.0f} M€" for side in monthly.columns]
        monthly.plot(kind="bar", stacked=True, ax=ax2,
                     color=[IC_SIDE_COLORS["export"], IC_SIDE_COLORS["import"]], width=0.7, alpha=0.8)
        ax2.set_xticklabels(pd.to_datetime(monthly.index, format="%m").strftime("%b"), rotation=0)
        ax2.set_xlabel("")
        ax2.set_ylabel("Gain from trade [M€]")
        ax2.set_title("Monthly gain")
        ax2.axhline(0, color="black", linewidth=0.8)
        ax2.legend(frameon=False)
        ax2.grid(True, axis="y", linestyle="--", linewidth=0.5, color="black", alpha=0.25)

        fig.suptitle(f"Gain from trade with {country}, valued at Spanish nodal prices: {total.sum():+.0f} M€",
                     fontsize=13)
        plt.tight_layout()

    #################### Table
    return (
        pd.DataFrame(rows).T
        .style.set_caption("Gain from trade [M€], valued at Spanish nodal prices.")
        .format("{:+.1f}")
    )
