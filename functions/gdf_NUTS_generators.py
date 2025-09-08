

import pandas as pd
import geopandas as gpd

from .gdf_network_generators import gdf_network_generators


def gdf_NUTS_generators(carrier, n, gdf_regions, gdf_NUTS, resource_class):
    """
    This function provides a gdf of a network with some generation features 
    aggregated at NUTS level for a specific carrier.

    Appropriate region and NUTS files are required.

    Columns:
      - geometry
      - NUTS_ID
      - area_NUTS
      - p_nom_NUTS               : installed capacity [MW]
      - p_nom_density_NUTS       : ratio between p_nom_NUTS and area_NUTS [MW/km2]
      - p_nom_max_NUTS           : potential according to land availability [MW]
      - p_nom_max_density_NUTS   : ratio between p_nom_max_NUTS and area_NUTS [MW/km2]
      - p_nom_max_ratio_NUTS     : ration between p_nom_NUTS and p_nom_max_NUTS [-]
      - p_nom_opt_NUTS           : optimal capacity [MW]
      - p_nom_opt_density_NUTS   : ratio between p_nom_opt_NUTS and area_NUTS [MW/km2]
      - p_nom_opt_max_ratio_NUTS : ration between p_nom_opt_NUTS and p_nom_max_NUTS [-]

    The gdf is provided in Plate Carrée crs('4036')    
    """

    gdf_network = gdf_network_generators(carrier, n, gdf_regions, resource_class)
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
    # Get p_nom_NUTS according to percentage of intersected areas
    intersected['p_nom_NUTS'] = intersected['p_nom'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell
    # Get p_nom_max_NUTS according to percentage of intersected areas
    intersected['p_nom_max_NUTS'] = intersected['p_nom_max'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell
    # Get p_nom_opt_NUTS according to percentage of intersected areas
    intersected['p_nom_opt_NUTS'] = intersected['p_nom_opt'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell0

    df_p_nom_NUTS = intersected.groupby('NUTS_ID')['p_nom_NUTS'].sum().reset_index()
    df_p_nom_max_NUTS = intersected.groupby('NUTS_ID')['p_nom_max_NUTS'].sum().reset_index()
    df_p_nom_opt_NUTS = intersected.groupby('NUTS_ID')['p_nom_opt_NUTS'].sum().reset_index()


    ##### Merge gdf_NUTS and df_p_nom_NUTS, df_p_nom_max_NUTS, df_p_nom_opt_NUTS
    gdf = pd.merge(gdf_NUTS, df_p_nom_NUTS, on='NUTS_ID')
    gdf = pd.merge(gdf, df_p_nom_max_NUTS, on='NUTS_ID')
    gdf = pd.merge(gdf, df_p_nom_opt_NUTS, on='NUTS_ID')

    # Add more columns
    gdf['p_nom_density_NUTS'] = gdf['p_nom_NUTS'] / gdf['area_NUTS']
    gdf['p_nom_max_density_NUTS'] = gdf['p_nom_max_NUTS'] / gdf['area_NUTS']
    gdf['p_nom_max_ratio_NUTS'] = gdf['p_nom_NUTS'] / gdf['p_nom_max_NUTS']
    gdf['p_nom_opt_density_NUTS'] = gdf['p_nom_opt_NUTS'] / gdf['area_NUTS']
    gdf['p_nom_opt_max_ratio_NUTS'] = gdf['p_nom_opt_NUTS'] / gdf['p_nom_max_NUTS']
    
    gdf = gdf.to_crs('4036')



    return gdf


