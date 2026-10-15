import matplotlib.pyplot as plt
import pandas as pd


def summary_system_costs(n, units: str = "bnEUR", top: int = 15):
    """System costs per component and carrier, from n.statistics (solved network).

    Columns:
      - capex : annualised capital cost of the optimal capacity (n.statistics.capex),
                including the capacity that already existed
      - opex  : operational cost of the dispatch (n.statistics.opex); negative values
                are revenues (e.g. electricity exports with negative marginal cost)
      - total : capex + opex (their sum over all rows is n.statistics.system_cost)

    Costs are for the modelled period (one year when the snapshots cover a full year).
    Draws a stacked bar plot of the ``top`` rows with the largest total and returns a
    styled table, in ``units`` (EUR | MEUR | bnEUR), sorted by total (descending).
    Rows with zero cost are dropped.
    """
    factors = {"EUR": 1, "MEUR": 1e6, "bnEUR": 1e9}
    if units not in factors:
        raise ValueError(f"units must be one of {list(factors)}, got {units!r}")

    S = n.statistics
    df = pd.concat(
        {"capex": S.capex(nice_names=False), "opex": S.opex(nice_names=False)}, axis=1
    ).fillna(0.0) / factors[units]
    df["total"] = df["capex"] + df["opex"]
    df = df.loc[df["total"].abs() > 0].sort_values("total", ascending=False)
    df.index.names = ["component", "carrier"]

    #################### Bar plot (top rows by total)
    df_top = df.head(top).droplevel("component").iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 0.4 * len(df_top) + 1))
    df_top[["capex", "opex"]].plot(kind="barh", stacked=True, ax=ax,
                                   color={"capex": "#08306b", "opex": "#6baed6"})
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel(f"Cost [{units}]")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_title(f"System cost: {df['total'].sum():.2f} {units} (top {len(df_top)} carriers)")
    plt.tight_layout()

    #################### Table
    return (
        df.style.set_caption(f"System costs [{units}] per component and carrier.")
        .format("{:.3f}")
    )
