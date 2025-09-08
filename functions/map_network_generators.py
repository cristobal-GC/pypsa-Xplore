

from .gdf_network_generators import gdf_network_generators



def map_network_generators(carrier, n, feature, ax, gdf_regions, resource_class, params, params_local):
    """
    This function plots generation features for a specific carrier
    in the geometry of a network.

    Features:
      - area
      - p_nom               : installed capacity [MW]
      - p_nom_density       : ratio between p_nom and area [MW/km2]
      - p_nom_max           : potential according to land availability [MW]
      - p_nom_max_density   : ratio between p_nom_max and area [MW/km2]
      - p_nom_max_ratio     : ration between p_nom and p_nom_max [-]
      - p_nom_opt           : optimal capacity [MW]
      - p_nom_opt_density   : ratio between p_nom_opt and area [MW/km2]
      - p_nom_opt_max_ratio : ration between p_nom_opt and p_nom_max [-]
    """

    gdf = gdf_network_generators(carrier, n, gdf_regions, resource_class)



    ##### Fix params_local
    if not params_local['vmin']:
        params_local['vmin'] = gdf[feature].min()

    if not params_local['vmax']:
        params_local['vmax'] = gdf[feature].max()



    ##### Plot in map
    gdf.plot(ax=ax, column=feature, 
             cmap=params['cmap'], edgecolor=params['edgecolor'], lw=params['lw'],
             vmin=params_local['vmin'], vmax=params_local['vmax'], 
             legend=True)


    if feature=='area':
        total = gdf[feature].sum()
        ax.set_title(f'Area. Total: {total:.2f} km2')

    if feature=='p_nom':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Installed capacity. Total: {total:.2f} MW')        

    if feature=='p_nom_density':
        ax.set_title(f'{carrier} : Installed capacity density [MW/km2]')

    if feature=='p_nom_max':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Potential. Total: {total:.2f} MW')    

    if feature=='p_nom_max_density':
        ax.set_title(f'{carrier} : Potential density [MW/km2]')                    

    if feature=='p_nom_max_ratio':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : ratio installed capacity / potential') 

    if feature=='p_nom_opt':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Optimal capacity. Total: {total:.2f} MW')  

    if feature=='p_nom_opt_density':
        ax.set_title(f'{carrier} : Optimal capacity density [MW/km2]')                      

    if feature=='p_nom_opt_max_ratio':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : ratio optimal capacity / potential') 
