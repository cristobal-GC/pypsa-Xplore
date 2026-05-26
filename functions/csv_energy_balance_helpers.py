"""Helpers for the energy_balance notebook.

Encapsulates the per-group transformation pipeline (Link losses merge,
charger/discharger merge) and the global cross-group threshold decision so
the notebook can keep its parameter and plotting cells short and readable.
"""

import re

import pandas as pd


def assign_group(bus_carrier, dic_group, warn=True):
    """Map a bus_carrier value to one of the keys of dic_group.

    Returns 'not_assigned' (and optionally prints a warning) when no group
    matches. We deliberately avoid the name 'other' because the plotting layer
    uses 'others' for the per-group aggregation of sub-threshold rows, and the
    two concepts are different.
    """
    for group, carriers in dic_group.items():
        if bus_carrier in carriers:
            return group
    if warn:
        print(
            f"[Warning] bus_carrier {bus_carrier!r} not found in any group of dic_group. "
            "Assigned to 'not_assigned'."
        )
    return 'not_assigned'


def _charger_key(s):
    return re.sub(r'\bdischarger\b', 'charger', s)


def _strip_charger(s):
    return re.sub(r'\s*\bcharger\b\s*', ' ', s).strip()


def process_group(df, group):
    """Per-group transforms: filter by group + Link-losses merge + charger/discharger merge.

    Does NOT apply any threshold; that decision is global and lives in
    :func:`apply_global_threshold`. The merged rows inherit the 'order' (CSV
    position) of the first row of each merge group, so a downstream sort by
    'order' preserves the original CSV layout.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataframe with columns ['component', 'carrier', 'bus_carrier',
        'value', 'group', 'order'].
    group : str
        Name of the group to process.

    Returns
    -------
    pd.DataFrame
        Processed dataframe for that group, with the same columns as `df`.
    """
    df_group = df[df['group'] == group].copy()

    # --- Merge Link rows sharing the same carrier into a single 'losses' row.
    # Rationale: in energy_balance.csv a Link with input on one bus and output
    # on another bus shows up as TWO rows with the SAME carrier — e.g. a
    # battery charger has one row on bus 'AC' (negative, input) and one on
    # bus 'battery' (positive, output). When both buses fall in the same group
    # the rows collapse into a single bar whose value equals the net
    # (input - |output|), i.e. the conversion losses of that Link.
    #
    # A Link can also have multiple INPUTS (all negative) or multiple OUTPUTS
    # (all positive) within the same group — e.g. DAC consumes both
    # 'urban central heat' and 'urban decentral heat'. Those rows are NOT a
    # losses pair: merging them would be misleading.
    #
    # Heuristic: merge only when the values have MIXED SIGNS (at least one
    # positive and one negative). Generic rule that avoids hardcoding carrier
    # names. The merged row inherits the 'order' of the first row.
    _links = df_group[df_group['component'] == 'Link']
    _to_merge_link = {}  # carrier -> list of df indices to merge
    for carrier, grp in _links.groupby('carrier', sort=False):
        if len(grp) < 2:
            continue
        vals = grp['value'].values
        if (vals > 0).any() and (vals < 0).any():
            _to_merge_link[carrier] = grp.index.tolist()

    _merged_rows = {
        carrier: {
            'component': 'Link',
            'carrier': carrier + ' losses',
            'bus_carrier': '+'.join(df_group.loc[idxs, 'bus_carrier'].values),
            'value': float(df_group.loc[idxs, 'value'].sum()),
            'group': df_group.loc[idxs[0], 'group'],
            'order': int(df_group.loc[idxs[0], 'order']),
        }
        for carrier, idxs in _to_merge_link.items()
    }
    _skip_link = {i for idxs in _to_merge_link.values() for i in idxs[1:]}
    _first_to_carrier = {idxs[0]: carrier for carrier, idxs in _to_merge_link.items()}

    _rows = []
    for idx, row in df_group.iterrows():
        if idx in _skip_link:
            continue
        if idx in _first_to_carrier:
            _rows.append(_merged_rows[_first_to_carrier[idx]])
        else:
            _rows.append(row.to_dict())
    df_group = pd.DataFrame(_rows, columns=df_group.columns).reset_index(drop=True)

    # --- Combine rows whose carrier differs only in 'charger' vs 'discharger'.
    # The first row of each pair survives (row.to_dict() preserves its 'order')
    # and the rest are dropped — so 'order' is naturally inherited.
    df_group['_key'] = df_group['carrier'].apply(_charger_key)

    _to_merge = {}
    for name, grp in df_group.groupby(['component', 'group', '_key'], sort=False):
        if len(grp) < 2:
            continue
        carriers = grp['carrier'].tolist()
        if any('charger' in c for c in carriers) and any('discharger' in c for c in carriers):
            _to_merge[name] = grp.index.tolist()
            print(
                f"[{group}][Merge charger/discharger] component='{name[0]}' | "
                f"{carriers} -> value sum = {grp['value'].sum():.3e}"
            )

    _merged_val   = {key: df_group.loc[idxs, 'value'].sum() for key, idxs in _to_merge.items()}
    _skip         = {idx for idxs in _to_merge.values() for idx in idxs[1:]}
    _first_to_key = {idxs[0]: key for key, idxs in _to_merge.items()}

    _rows = []
    for idx, row in df_group.iterrows():
        if idx in _skip:
            continue
        d = row.to_dict()
        if idx in _first_to_key:
            key = _first_to_key[idx]
            d['value'] = _merged_val[key]
            d['carrier'] = _strip_charger(key[2])  # key = (component, group, _key)
        _rows.append(d)
    df_group = (
        pd.DataFrame(_rows, columns=df_group.columns)
        .drop(columns=['_key'])
        .reset_index(drop=True)
    )

    return df_group


def apply_global_threshold(pre_dfs, group_threshold, sentinel_order):
    """Apply the cross-group threshold rule.

    A (component, carrier) is kept in every group where it appears as long as
    it passes the group's threshold in AT LEAST ONE of those groups. Keys that
    never pass are aggregated per-group into a synthetic 'others' row whose
    order is `sentinel_order` (so it sorts after every real CSV row).

    Parameters
    ----------
    pre_dfs : dict[str, pd.DataFrame]
        Per-group processed dataframes (output of :func:`process_group`).
    group_threshold : dict[str, float | None]
        Mapping group -> threshold value. Groups absent from the dict (or with
        value `None`) are not filtered.
    sentinel_order : int
        Order value assigned to the synthetic 'others' row. Use any integer
        greater than the largest real `order` (typically `len(df)`).

    Returns
    -------
    dict[str, pd.DataFrame]
    """
    # Build the set of significant (component, carrier) keys across all groups
    significant_keys = set()
    for g, df_g in pre_dfs.items():
        thr = group_threshold.get(g)
        if thr is None:
            for _, row in df_g.iterrows():
                significant_keys.add((row['component'], row['carrier']))
        else:
            passing = df_g[df_g['value'].abs() >= thr]
            for _, row in passing.iterrows():
                significant_keys.add((row['component'], row['carrier']))

    out = {}
    for g, df_g in pre_dfs.items():
        if df_g.empty:
            out[g] = df_g.reset_index(drop=True)
            continue

        keep_mask = df_g.apply(
            lambda r: (r['component'], r['carrier']) in significant_keys, axis=1
        )
        dropped = df_g[~keep_mask]
        df_kept = df_g[keep_mask].reset_index(drop=True)

        if not dropped.empty:
            others_value = float(dropped['value'].sum())
            thr = group_threshold.get(g)
            thr_str = f"{thr:g}" if thr is not None else "n/a"
            print(
                f"[{g}][Threshold filter] {len(dropped)} row(s) sub-threshold here AND "
                f"in every other group where they appear -> aggregated into 'others' "
                f"(sum = {others_value:+.3e}, threshold={thr_str}):"
            )
            for _, r in dropped.iterrows():
                print(f"  - {r['component']:>10} | {r['carrier']:<40} | {r['value']:+.3e}")

            others_row = pd.DataFrame([{
                'component': '',
                'carrier': 'others',
                'bus_carrier': '',
                'value': others_value,
                'group': g,
                'order': sentinel_order,
            }])
            df_kept = pd.concat([df_kept, others_row], ignore_index=True)

        out[g] = df_kept

    return out
