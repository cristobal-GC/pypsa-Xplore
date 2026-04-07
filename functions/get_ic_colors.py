from collections import Counter

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def get_ic_colors(columns, country_colormaps=None):
    """Assign a hex color to each interconnection column based on country.

    Each country is mapped to a colormap and receives evenly-spaced shades
    — one shade per link belonging to that country.  Unrecognised columns
    fall back to grey.

    Parameters
    ----------
    columns : list-like
        Column names of the interconnection DataFrame (e.g. from
        ``n.links_t['p0'].filter(like='export').columns``).
    country_colormaps : dict, optional
        Mapping ``{country_code_lower: matplotlib_colormap}``.
        Defaults to ``{'pt': plt.cm.Greens, 'fr': plt.cm.Blues}``.

    Returns
    -------
    dict
        ``{column_name: hex_color}``

    Examples
    --------
    >>> ic_color_dict = get_ic_colors(combined.columns)
    >>> colors = [ic_color_dict[col] for col in combined.columns]
    """
    if country_colormaps is None:
        country_colormaps = {
            "pt": plt.cm.Greens,
            "fr": plt.cm.Blues,
        }

    # Match each column to a country key
    col_country = {}
    for col in columns:
        col_lower = col.lower()
        matched = next(
            (country for country in country_colormaps if country in col_lower),
            None,
        )
        col_country[col] = matched

    # Count links per country to size the shade range
    country_counts = Counter(v for v in col_country.values() if v is not None)

    # Build an iterator of shades for each country
    country_shade_iters = {}
    for country, cmap in country_colormaps.items():
        n = country_counts.get(country, 0)
        if n > 0:
            shades = [
                mcolors.to_hex(c) for c in cmap(np.linspace(0.45, 0.85, n))
            ]
            country_shade_iters[country] = iter(shades)

    # Assign final color per column
    color_dict = {}
    for col in columns:
        country = col_country[col]
        if country and country in country_shade_iters:
            color_dict[col] = next(country_shade_iters[country])
        else:
            color_dict[col] = "#808080"

    return color_dict
