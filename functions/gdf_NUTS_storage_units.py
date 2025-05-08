

import pandas as pd
import geopandas as gpd

from .gdf_network_storage_units import gdf_network_storage_units


def gdf_NUTS_storage_units(carrier, n, gdf_regions, gdf_NUTS):
    """
    This function provides a gdf of a network with some storage unit features 
    aggregated at NUTS level for a specific carrier.

    Appropriate region and NUTS files are required.

    Columns:
      - geometry
      - NUTS_ID
      - area_NUTS      
      - p_nom_NUTS               : installed capacity [MW]
      - p_nom_density_NUTS       : ratio between p_nom and area [MW/km2]
      - p_nom_opt_NUTS           : optimal capacity [MW]
      - p_nom_opt_density_NUTS   : ratio between p_nom_opt and area [MW/km2]
      - max_hours_NUTS			 : ratio between energy store capacity and power capacity

    The gdf is provided in Plate Carrée crs('4036')    
    """

    gdf_network = gdf_network_storage_units(carrier, n, gdf_regions)
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
    intersected['p_nom_opt_NUTS'] = intersected['p_nom_opt'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell0
    # Get max_hours_NUTS according to percentage of intersected areas
    intersected['max_hours_NUTS'] = intersected['max_hours'] * (intersected['area_intersection'] / intersected['area']) # 'area' refers to Voronoi cell0

    df_p_nom_NUTS = intersected.groupby('NUTS_ID')['p_nom_NUTS'].sum().reset_index()
    df_p_nom_opt_NUTS = intersected.groupby('NUTS_ID')['p_nom_opt_NUTS'].sum().reset_index()
    df_max_hours_NUTS = intersected.groupby('NUTS_ID')['max_hours_NUTS'].mean().reset_index()


    ##### Merge gdf_NUTS and df_p_nom_NUTS, df_p_nom_opt_NUTS, df_max_hours_NUTS
    gdf = pd.merge(gdf_NUTS, df_p_nom_NUTS, on='NUTS_ID')
    gdf = pd.merge(gdf, df_p_nom_opt_NUTS, on='NUTS_ID')
    gdf = pd.merge(gdf, df_max_hours_NUTS, on='NUTS_ID')

    # Add more columns
    gdf['p_nom_density_NUTS'] = gdf['p_nom_NUTS'] / gdf['area_NUTS']
    gdf['p_nom_opt_density_NUTS'] = gdf['p_nom_opt_NUTS'] / gdf['area_NUTS']
    
    gdf = gdf.to_crs('4036')



    return gdf


