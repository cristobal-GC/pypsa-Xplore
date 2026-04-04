

from .gdf_NUTS_links import gdf_NUTS_links



def map_NUTS_links(carrier, n, feature, ax, gdf_regions, gdf_NUTS, params, params_local):
    """
    This function plots a generation features for a specific carrier
    aggregated to NUTS level.

    Features:
      - area_NUTS
      - p_nom_NUTS              : installed capacity [MW]      
      - p_nom_opt_NUTS          : optimal capacity [MW]
      - p_nom_e_NUTS            : installed capacity [MW] (includes link efficiency if required)     
      - p_nom_e_opt_NUTS        : optimal capacity [MW] (includes link efficiency if required)
    """

    gdf = gdf_NUTS_links(carrier, n, gdf_regions, gdf_NUTS)



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

    if feature=='p_nom_e_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Installed capacity. Total: {total:.2f} MW')        

    if feature=='p_nom_e_opt_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Optimal capacity. Total: {total:.2f} MW')  

