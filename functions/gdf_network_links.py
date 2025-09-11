

import pandas as pd
import geopandas as gpd



def gdf_network_links(carrier, n, gdf_regions):
    """
    This function provides a gdf of a network with some link features 
    for one of the following carriers:
      - CCGT
      - OCGT
      - H2 Electrolysis
      - H2 electrolysis
      - H2 Fuel Cell
      - H2 fuel cell
      - battery charger
      - battery discharger
      - H2 turbine

    An appropriate region file is required.

    Columns:
      - geometry
      - carrier
      - area
      - bus0        : initial point
      - bus1        : end point
      - bus         : one of the two above, the one related to the geometry regions
      - efficiency  : to consider for example for CCGT capacity
      - p_nom       : installed capacity [MW]
      - p_nom_opt   : optimal capacity [MW]
      - p_nom_e     : installed capacity [MW] (includes link efficiency if required)
      - p_nom_e_opt : optimal capacity [MW] (includes link efficiency if required)

    The gdf is provided in Plate Carrée crs('4036')    
    """

    ##### Get df with generators info
    lk = n.links
    # filter carrier
    df = lk[lk['carrier']==carrier]
    # select some relevant columns
    df = df[['carrier', 'bus0', 'bus1', 'efficiency', 'p_nom', 'p_nom_opt']]
    # add column 'bus' according to the link direction for the selected carrier. 
    # Also, create column 'p_nom_e' and 'p_nom_e_opt' for electric capacity.
    if carrier in ['CCGT', 'OCGT', 'H2 Fuel Cell', 'H2 fuel cell', 'battery discharger', 'H2 turbine']:
        df['bus'] = df['bus1']
        df['p_nom_e'] = df['p_nom']*df['efficiency']
        df['p_nom_e_opt'] = df['p_nom_opt']*df['efficiency']
    if carrier in ['H2 Electrolysis', 'H2 electrolysis', 'battery charger']:
        df['bus'] = df['bus0']
        df['p_nom_e'] = df['p_nom']
        df['p_nom_e_opt'] = df['p_nom_opt']


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



