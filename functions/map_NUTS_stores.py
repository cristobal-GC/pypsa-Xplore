

from .gdf_NUTS_stores import gdf_NUTS_stores



def map_NUTS_stores(carrier, n, feature, ax, gdf_regions, gdf_NUTS, params, params_local):
    """
    This function plots a store features for a specific carrier
    aggregated to NUTS level.

    Features:
      - area_NUTS
      - e_nom_opt_NUTS            : optimal energy capacity [GWh]
    """

    gdf = gdf_NUTS_stores(carrier, n, gdf_regions, gdf_NUTS)



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

    if feature=='e_nom_opt_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Optimal energy storage. Total: {total:.2f} GWh')


