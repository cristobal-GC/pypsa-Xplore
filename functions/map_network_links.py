

from .gdf_network_links import gdf_network_links



def map_network_links(carrier, n, feature, ax, gdf_regions, params, params_local):
    """
    This function plots link features for a specific carrier
    in the geometry of a network.

    Features:
      - area
      - p_nom_e               : installed capacity [MWe] (includes link efficiency if required)    
      - p_nom_e_opt           : optimal capacity [MWe] (includes link efficiency if required)
    """

    gdf = gdf_network_links(carrier, n, gdf_regions)



    ##### Fix params_local
    if not params_local['vmin']:
        params_local['vmin'] = gdf[feature].min()

    if not params_local['vmax']:
        params_local['vmax'] = gdf[feature].max()



    ##### Plot in map
    gdf.plot(ax=ax, column=feature, 
             cmap=params['cmap'], edgecolor=params['edgecolor'],
             vmin=params_local['vmin'], vmax=params_local['vmax'], 
             legend=True)


    if feature=='area':
        total = gdf[feature].sum()
        ax.set_title(f'Area. Total: {total:.2f} km2')

    if feature=='p_nom_e':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Installed capacity. Total: {total:.2f} MW')        

    if feature=='p_nom_e_opt':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Optimal capacity. Total: {total:.2f} MW')  

