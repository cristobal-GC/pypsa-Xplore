

import pandas as pd
import geopandas as gpd



def gdf_network_stores(carrier, n, gdf_regions):
    """
    This function provides a gdf of a network with some store features 
    for a specific carrier.

    An appropriate region file is required.

    Columns:
      - geometry
      - bus_original	: is the bus defined in n.stores
      - bus				: is the corresponding network bus map-located
      - carrier
      - area
      - e_nom_opt       : optimal energy capacity [GWh]

    The gdf is provided in Plate Carrée crs('4036')    
    """

    ##### Get df with generators info
    st = n.stores
    # filter carrier
    df = st[st['carrier']==carrier]
    # select some relevant columns
    df = df[['carrier', 'bus', 'e_nom_opt']]
    # Put in GWh
    df['e_nom_opt'] = df['e_nom_opt'].div(1e3)
    # place 'bus' in 'bus_original', and create 'bus' from column index and removing white space + carrier
    # this is to have the samen bus names as in the gdf_regions
    df.rename(columns={'bus': 'bus_original'}, inplace=True)
    df['bus'] = df.index.to_series().apply(lambda x: x.replace(' '+carrier,''))



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



    return gdf



