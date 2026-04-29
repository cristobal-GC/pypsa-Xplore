

from .gdf_network_loadst_pset import gdf_network_loadst_pset



def map_network_loadst_pset(
    n,
    feature,
    ax,
    gdf_regions,
    params,
    params_local,
    load_patterns=None,
    load_key=None,
):
    """
    This function plots load features in the geometry of a network.

    Features:
      - area
      - annual_load         : [TWh]
      - annual_load_density : [GWh/km2]      
    """

    gdf = gdf_network_loadst_pset(
        n,
        gdf_regions,
        load_patterns=load_patterns,
        load_key=load_key,
    )



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


    if feature=='area':
        total = gdf[feature].sum()
        ax.set_title(f'Area. Total: {total:.2f} km2')

    if feature=='annual_load':
        total = gdf[feature].sum()
        ax.set_title(f'Annual load. Total: {total:.2f} TWh')        

    if feature=='annual_load_density':
        ax.set_title(f'Annual load density [GWh/km2]')



