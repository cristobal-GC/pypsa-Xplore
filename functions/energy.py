

def snapshot_hours(n):
    """Hours represented by each snapshot, taken from ``n.snapshot_weightings``.

    Weighting a power [MW] time series by these hours yields energy [MWh], which is
    correct for **any** temporal resolution. Summing the raw power instead is only
    valid when every snapshot represents exactly one hour.

    Returns a pandas Series indexed by snapshot (robust across PyPSA versions, where
    ``snapshot_weightings`` may be a DataFrame with an 'generators' column or a Series).
    """
    sw = n.snapshot_weightings
    if hasattr(sw, "columns"):
        col = "generators" if "generators" in sw.columns else sw.columns[0]
        return sw[col]
    return sw
