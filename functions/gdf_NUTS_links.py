

import pandas as pd
import geopandas as gpd

from .gdf_network_links import gdf_network_links


def gdf_NUTS_links(carrier, n, gdf_regions, gdf_NUTS):
    """
    This function provides a gdf of a network with some link features 
    aggregated at NUTS level for a specific carrier.

    Appropriate region and NUTS files are required.

    Columns:
      - geometry
      - NUTS_ID
      - area_NUTS
      - p_nom_NUTS               : installed capacity [MW]
      - p_nom_opt_NUTS           : optimal capacity [MW]
      - p_nom_e_NUTS             : installed capacity [MW] (includes link efficiency if required)
      - p_nom_e_opt_NUTS         : optimal capacity [MW] (includes link efficiency if required)

    The gdf is provided in Plate Carrée crs('4036')    
    """

    gdf_network = gdf_network_links(carrier, n, gdf_regions)
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
    # Get p_nom_opt_NUTS according to percentage of intersected areas
    intersected['p_nom_opt_NUTS'] = intersected['p_nom_opt'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell
    # Get p_nom_e_NUTS according to percentage of intersected areas
    intersected['p_nom_e_NUTS'] = intersected['p_nom_e'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell
    # Get p_nom_e_opt_NUTS according to percentage of intersected areas
    intersected['p_nom_e_opt_NUTS'] = intersected['p_nom_e_opt'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell

    df_p_nom_NUTS = intersected.groupby('NUTS_ID')['p_nom_NUTS'].sum().reset_index()
    df_p_nom_opt_NUTS = intersected.groupby('NUTS_ID')['p_nom_opt_NUTS'].sum().reset_index()
    df_p_nom_e_NUTS = intersected.groupby('NUTS_ID')['p_nom_e_NUTS'].sum().reset_index()
    df_p_nom_e_opt_NUTS = intersected.groupby('NUTS_ID')['p_nom_e_opt_NUTS'].sum().reset_index()


    ##### Merge gdf_NUTS and df_p_nom_NUTS, df_p_nom_opt_NUTS, df_p_nom_e_NUTS, df_p_nom_e_opt_NUTS
    gdf = pd.merge(gdf_NUTS, df_p_nom_NUTS, on='NUTS_ID')
    gdf = pd.merge(gdf, df_p_nom_opt_NUTS, on='NUTS_ID')
    gdf = pd.merge(gdf, df_p_nom_e_NUTS, on='NUTS_ID')
    gdf = pd.merge(gdf, df_p_nom_e_opt_NUTS, on='NUTS_ID')


    
    gdf = gdf.to_crs('4036')



    return gdf


