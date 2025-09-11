

import pandas as pd
import geopandas as gpd



def gdf_network_generatorst_p(carrier, n, gdf_regions, resource_class):
    """
    This function provides a gdf of a network with some generation_t features based on p (after dispatch)
    for a specific carrier.

    For solar and wind carriers, there are classes.

    An appropriate region file is required.

    Columns:
      - geometry
      - bus
      - carrier
      - area
      - AEP                  : Annual Energy Production [TWh]

    The gdf is provided in Plate Carrée crs('4036')    
    """

    ##### Get df with generationt_p info, and for the selected carrier
    ggt_p = n.generators_t['p'].filter(like=carrier, axis=1)
    df = ggt_p.sum().to_frame(name='AEP').div(1e6)   # TWh 
    # Add bus column taken from n.generators
    df['bus'] = n.generators.loc[df.index]['bus']
   
    ##### Modifications to addapt renewable classes (only for onwind, offwind-float, offwind-ac, offwind-dc, solar, solar-hsat
    if ('wind' in carrier or 'solar' in carrier):
        ## If class was defined, filter only rows with this class
        if isinstance(resource_class, int):
            ### Define index pattern (ends in '... resource_class carrier')
            pat = fr"\b{resource_class}\s+{carrier}$"
            ### Filter to keep only this class
            df = df[df.index.str.contains(pat, regex=True)]
        ## If 'all' classes was defined, add rows by bus, and re-build the dataframe to fit the required columns
        elif resource_class == 'all':
            df = df.groupby("bus", as_index=False)[["AEP"]].sum()
            df['carrier'] = carrier
            df.index = df["bus"] + " " + df["carrier"]
            df.index.name = 'Generator'
        else:
            raise ValueError(f"Incorrect value for 'resource_class'")



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



