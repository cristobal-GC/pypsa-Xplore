

import pandas as pd
import geopandas as gpd



def gdf_network_loadst_pset(n, gdf_regions):
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
    df = lot_pset.sum().to_frame(name='annual_load')    
    # Put in TWh
    df['annual_load'] = df['annual_load'].div(1e6)
    # Add column 'bus'
    df['bus'] = df.index


    ##### Get gdf0 with regions 
    gdf0 = gdf_regions.copy()
    gdf0.rename(columns={'name': 'bus'}, inplace=True)
    # Select just some columns
    gdf0 = gdf0[['bus', 'geometry']]
    # Add area [km2]
    gdf0_area = gdf0.to_crs(3035)
    gdf0['area'] = gdf0_area.area/1e6

 
    ##### Merge df and gdf0
    gdf = pd.merge(gdf0,df, on='bus')

    ##### Add annual_load_density
    gdf['annual_load_density'] = gdf['annual_load'] / gdf['area']
    # Put in GWh/km2
    gdf['annual_load_density'] = gdf['annual_load_density']*1e3



    return gdf



