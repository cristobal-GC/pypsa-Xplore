

from .gdf_network_storage_units import gdf_network_storage_units



def map_network_storage_units(carrier, n, feature, ax, gdf_regions, params, params_local):
    """
    This function plots storage unit features for a specific carrier
    in the geometry of a network.

    Features:
      - area
      - p_nom               : installed capacity [MW]
      - p_nom_density       : ratio between p_nom and area [MW/km2]
      - p_nom_opt           : optimal capacity [MW]
      - p_nom_opt_density   : ratio between p_nom_opt and area [MW/km2]
      - max_hours			: ratio between energy store capacity and power capacity
    """

    gdf = gdf_network_storage_units(carrier, n, gdf_regions)



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

    if feature=='p_nom':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Installed capacity. Total: {total:.2f} MW')        

    if feature=='p_nom_density':
        ax.set_title(f'{carrier} : Installed capacity density [MW/km2]')

    if feature=='p_nom_opt':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Optimal capacity. Total: {total:.2f} MW')  

    if feature=='p_nom_opt_density':
        ax.set_title(f'{carrier} : Optimal capacity density [MW/km2]')   

    if feature=='max_hours':
        ax.set_title(f'{carrier} : Maximum hours (storage/capacity) [h]') 

  

  
