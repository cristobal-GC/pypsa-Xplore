

import pandas as pd
import re

from .filter_columns import filter_df_columns
from .filter_columns import get_column_patterns



def gdf_network_loadst_pset(n, gdf_regions, load_patterns=None, load_key=None):
    """
    This function provides a gdf of a network with some load features.

    An appropriate region file is required.

    Columns:
      - geometry
      - bus
      - carrier
      - area
      - annual_load         : [TWh]
      - annual_load_density : [GWh/km2]      

    The gdf is provided in Plate Carrée crs('4326')    
    """

    ##### Get df with load info
    lot_pset = n.loads_t['p_set']

    # Select load columns by key or explicit patterns.
    lot_pset_filtered = filter_df_columns(
      lot_pset,
      filter_key=load_key,
      patterns=load_patterns,
    )
    selected_cols = lot_pset_filtered.columns

    if load_patterns is not None:
      used_patterns = load_patterns
    elif load_key is not None:
      used_patterns = get_column_patterns(load_key)
    else:
      used_patterns = None

    # Keep only load columns that exist in n.loads index
    valid_cols = [col for col in selected_cols if col in n.loads.index]

    # Aggregate annual load by bus and convert to TWh
    if len(valid_cols) > 0:
      df_load = lot_pset[valid_cols].sum(axis=0).to_frame(name='annual_load')
      df_load['bus'] = n.loads.loc[valid_cols, 'bus'].astype(str).values

      # Electricity loads are often attached to "... low voltage" buses,
      # while region names use the base bus label.
      if load_key is not None and str(load_key).strip().lower() == 'electricity':
        df_load['bus'] = df_load['bus'].str.replace(
          r'\s*low\s+voltage\s*$',
          '',
          regex=True,
          flags=re.IGNORECASE,
        )

      # For sector loads (e.g. "... urban central heat"), map to base region bus.
      if used_patterns:
        pattern_regex = '|'.join(re.escape(pattern) for pattern in used_patterns)
        df_load['bus'] = df_load['bus'].str.replace(
          rf'\s*(?:{pattern_regex})\s*$',
          '',
          regex=True,
          flags=re.IGNORECASE,
        )

      df = df_load.groupby('bus', as_index=False)['annual_load'].sum()
      df['annual_load'] = df['annual_load'].div(1e6)
    else:
      df = pd.DataFrame(columns=['bus', 'annual_load'])


    ##### Get gdf0 with regions 
    gdf0 = gdf_regions.copy()
    gdf0.rename(columns={'name': 'bus'}, inplace=True)
    # Select just some columns
    gdf0 = gdf0[['bus', 'geometry']]
    # Add area [km2]
    gdf0_area = gdf0.to_crs(3035)
    gdf0['area'] = gdf0_area.area/1e6

 
    ##### Merge df and gdf0
    gdf = pd.merge(gdf0,df, on='bus', how='left')
    gdf['annual_load'] = gdf['annual_load'].fillna(0)

    ##### Add annual_load_density
    gdf['annual_load_density'] = gdf['annual_load'] / gdf['area']
    # Put in GWh/km2
    gdf['annual_load_density'] = gdf['annual_load_density']*1e3



    return gdf



