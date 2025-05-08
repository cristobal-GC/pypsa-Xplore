

import pandas as pd
import geopandas as gpd

from .gdf_network_loadst_pset import gdf_network_loadst_pset


def gdf_NUTS_loadst_pset(n, gdf_regions, gdf_NUTS):
    """
    This function provides a gdf of a network with some load features 
    aggregated at NUTS level.

    Appropriate region and NUTS files are required.

    Columns:
      - geometry
      - NUTS_ID
      - area_NUTS
      - annual_load_NUTS         : [TWh]
      - annual_load_density_NUTS : [GWh/km2]      

    The gdf is provided in Plate Carrée crs('4036')    
    """

    gdf_network = gdf_network_loadst_pset(n, gdf_regions)
    gdf_network = gdf_network.to_crs('3035')


    ##### gdf_NUTS, retain relevant columns and add area
    gdf_NUTS = gdf_NUTS[['NUTS_ID', 'geometry']]
    # Put in crs (3035)
    gdf_NUTS = gdf_NUTS.to_crs(3035)
    # Add area_NUTS [km2]
    gdf_NUTS['area_NUTS'] = gdf_NUTS.area/1e6


    ##### Make intersection, and group by NUTS
    intersected = gpd.overlay(gdf_network, gdf_NUTS, how='intersection')
    
    # Get intersected area
    intersected['area_intersection'] = intersected.geometry.area/1e6
    # Get annual_load_NUTS according to percentage of intersected areas
    intersected['annual_load_NUTS'] = intersected['annual_load'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell

    df_annual_load_NUTS = intersected.groupby('NUTS_ID')['annual_load_NUTS'].sum().reset_index()
    

    ##### Merge gdf_NUTS and df_annual_load_NUTS
    gdf = pd.merge(gdf_NUTS, df_annual_load_NUTS, on='NUTS_ID')
   
    # Add more columns
    gdf['annual_load_density_NUTS'] = gdf['annual_load_NUTS'] / gdf['area_NUTS']
   # Put in GWh/km2
    gdf['annual_load_density_NUTS'] = gdf['annual_load_density_NUTS']*1e3

    gdf = gdf.to_crs('4036')



    return gdf


