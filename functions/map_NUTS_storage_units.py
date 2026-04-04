

from .gdf_NUTS_storage_units import gdf_NUTS_storage_units



def map_NUTS_storage_units(carrier, n, feature, ax, gdf_regions, gdf_NUTS, params, params_local):
    """
    This function plots a storage unit features for a specific carrier
    aggregated to NUTS level.

    Features:
      - area_NUTS
      - p_nom_NUTS               : installed capacity [MW]
      - p_nom_density_NUTS       : ratio between p_nom and area [MW/km2]
      - p_nom_opt_NUTS           : optimal capacity [MW]
      - p_nom_opt_density_NUTS   : ratio between p_nom_opt and area [MW/km2]
      - max_hours_NUTS			 : ratio between energy store capacity and power capacity
    """

    gdf = gdf_NUTS_storage_units(carrier, n, gdf_regions, gdf_NUTS)



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

    if feature=='p_nom_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Installed capacity. Total: {total:.2f} MW')        

    if feature=='p_nom_density_NUTS':
        ax.set_title(f'{carrier} : Installed capacity density [MW/km2]')

    if feature=='p_nom_opt_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Optimal capacity. Total: {total:.2f} MW')  

    if feature=='p_nom_opt_density_NUTS':
        ax.set_title(f'{carrier} : Optimal capacity density [MW/km2]')                      

    if feature=='max_hours_NUTS':
        ax.set_title(f'{carrier} : Average maximum hours (storage/capacity) [h]') 

