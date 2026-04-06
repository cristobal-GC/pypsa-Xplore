

from .gdf_NUTS_loadst_pset import gdf_NUTS_loadst_pset



def map_NUTS_loadst_pset(n, feature, ax, gdf_regions, gdf_NUTS, params, params_local):
    """
    This function plots load features aggregated to NUTS level.

    Features:
      - area
      - annual_load         : [TWh]
      - annual_load_density : [GWh/km2] 
    """

    gdf = gdf_NUTS_loadst_pset(n, gdf_regions, gdf_NUTS)



    ##### Fix params_local
    vmin = params_local.get('vmin')
    vmax = params_local.get('vmax')

    if vmin in (None, ''):
        vmin = gdf[feature].min()

    if vmax in (None, ''):
        vmax = gdf[feature].max()
    
    
    
    ##### Plot in map
    gdf.plot(ax=ax, column=feature, 
             cmap=params['cmap'], edgecolor=params['edgecolor'], lw=params['lw'],
             vmin=vmin, vmax=vmax, 
             legend=True)


    if feature=='area_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'Area. Total: {total:.2f} km2')

    if feature=='annual_load_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'Annual load. Total: {total:.2f} TWh')        

    if feature=='annual_load_density_NUTS':
        ax.set_title(f'Annual load density [GWh/km2]')


