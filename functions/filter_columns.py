import pandas as pd


DEFAULT_COLUMN_PATTERNS_BY_KEY = {
    "heating": [
        "rural heat",
        "urban central heat",
        "urban decentral heat",
    ],
    # Keep only one token like "ESx" or two tokens like "ESx y".
    # Excludes names with extra words, e.g. "ESx y heat".
    "electricity": [
        "re_full:^ES\\S*(?:\\s+\\S+)?$",
    ],
}


def get_column_patterns(filter_key, patterns_by_key=None):
    """
    Return column-filter patterns associated with a key.

    Example:
        filter_key='heating' ->
        ['rural heat', 'urban central heat', 'urban decentral heat']
    """

    if filter_key is None:
        return None

    patterns_map = dict(DEFAULT_COLUMN_PATTERNS_BY_KEY)
    if patterns_by_key:
        patterns_map.update(patterns_by_key)

    key = str(filter_key).strip().lower()
    if key not in patterns_map:
        raise KeyError(f"Unknown filter_key '{filter_key}'. Available keys: {list(patterns_map)}")

    return list(patterns_map[key])


def filter_df_columns(df, filter_key=None, patterns=None, patterns_by_key=None):
    """
    Filter DataFrame columns using either:
      - a named key (filter_key), or
      - an explicit list of patterns (patterns).

        Matching rule:
            - default: column name contains ANY pattern (case-insensitive)
            - if pattern starts with 're_full:': full-string regex match
            - if pattern starts with 're:': regex contains-style match
    """

    if patterns is None and filter_key is not None:
        patterns = get_column_patterns(filter_key, patterns_by_key=patterns_by_key)

    if not patterns:
        return df.copy()

    mask = pd.Series(False, index=df.columns)
    for pattern in patterns:
        if isinstance(pattern, str) and pattern.startswith("re_full:"):
            regex = pattern[len("re_full:") :]
            mask = mask | df.columns.str.fullmatch(regex, case=False, na=False)
        elif isinstance(pattern, str) and pattern.startswith("re:"):
            regex = pattern[len("re:") :]
            mask = mask | df.columns.str.contains(regex, case=False, na=False, regex=True)
        else:
            mask = mask | df.columns.str.contains(pattern, case=False, na=False)

    return df.loc[:, mask].copy()
