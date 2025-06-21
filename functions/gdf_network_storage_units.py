

import pandas as pd
import geopandas as gpd



def gdf_network_storage_units(carrier, n, gdf_regions):
    """
    This function provides a gdf of a network with some storage unit features 
    for a specific carrier.

    An appropriate region file is required.

    Columns:
      - geometry
      - bus
      - carrier
      - area
      - p_nom               : installed capacity [MW]
      - p_nom_density       : ratio between p_nom and area [MW/km2]
      - p_nom_opt           : optimal capacity [MW]
      - p_nom_opt_density   : ratio between p_nom_opt and area [MW/km2]
      - max_hours			: ratio between energy store capacity and power capacity

    The gdf is provided in Plate Carrée crs('4036')    
    """

    ##### Get df with generators info
    su = n.storage_units
    # filter carrier
    df = su[su['carrier']==carrier]
    # select some relevant columns
    df = df[['carrier', 'bus', 'p_nom', 'p_nom_opt', 'max_hours']]



    ##### Get gdf0 with regions 
    gdf0 = gdf_regions.copy()
    gdf0.rename(columns={'name': 'bus'}, inplace=True)
    # Select just some columns
    gdf0 = gdf0[['bus', 'geometry']]
    # Add area [km2]
    gdf0_area = gdf0.to_crs(3035)
    gdf0['area'] = gdf0_area.area/1e6

 
    ##### Merge df and gdf0
    gdf =  pd.merge(gdf0,df, on='bus')

    ##### Add p_nom_density 
    gdf['p_nom_density'] = gdf['p_nom'] / gdf['area']

    ##### Add p_nom_opt_density 
    gdf['p_nom_opt_density'] = gdf['p_nom_opt'] / gdf['area']



    return gdf



