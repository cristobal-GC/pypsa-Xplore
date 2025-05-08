

import pandas as pd
import geopandas as gpd



def gdf_network_generatorst_pmaxpu(carrier, n, gdf_regions, gen_class):
    """
    This function provides a gdf of a network with some generation_t features
    for a specific carrier.

    An appropriate region file is required.

    Columns:
      - geometry
      - bus
      - carrier
      - area
      - CF                  : Annual capacity factor

    The gdf is provided in Plate Carrée crs('4036')    
    """

    ##### Get df with geerationt_pmaxpu info
    ggt_pmaxpu = n.generators_t['p_max_pu']
    df = ggt_pmaxpu.mean().to_frame(name='CF') 
   
    # Use multi-index with 'bus' and 'carrier'
    # Note that the index for onwind, solar is 'bus-class-carrier'
    # while for the rest is just 'bus-carrier'
    if ('wind' in carrier or 'solar' in carrier):        
        split_index = df.index.to_series().str.rsplit(' ', n=2, expand=True)
        df['bus'] = split_index[0].values
        df['gen_class'] = split_index[1].astype(int) # gen_class as integer
        df['carrier'] = split_index[2].values
    else:
        split_index = df.index.to_series().str.rsplit(' ', n=1, expand=True)
        df['bus'] = split_index[0].values
        df['carrier'] = split_index[1].values


    # filter carrier (and class, for wind, solar)
    if ('wind' in carrier or 'solar' in carrier):
        df = df[(df['carrier']==carrier) & (df['gen_class']==gen_class)]
    else:
        df = df[df['carrier']==carrier]
        


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



