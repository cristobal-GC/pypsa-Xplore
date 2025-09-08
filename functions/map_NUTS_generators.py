

from .gdf_NUTS_generators import gdf_NUTS_generators



def map_NUTS_generators(carrier, n, feature, ax, gdf_regions, gdf_NUTS, resource_class, params, params_local):
    """
    This function plots a generation features for a specific carrier
    aggregated to NUTS level.

    Features:
      - area_NUTS
      - p_nom_NUTS               : installed capacity [MW]
      - p_nom_density_NUTS       : ratio between p_nom_NUTS and area_NUTS [MW/km2]
      - p_nom_max_NUTS           : potential according to land availability [MW]
      - p_nom_max_density_NUTS   : ratio between p_nom_max_NUTS and area_NUTS [MW/km2]
      - p_nom_max_ratio_NUTS     : ration between p_nom_NUTS and p_nom_max_NUTS [-]
       - p_nom_opt_NUTS          : optimal capacity [MW]
      - p_nom_opt_density_NUTS   : ratio between p_nom_opt_NUTS and area_NUTS [MW/km2]
      - p_nom_opt_max_ratio_NUTS : ration between p_nom_opt_NUTS and p_nom_max_NUTS [-]
    """

    gdf = gdf_NUTS_generators(carrier, n, gdf_regions, gdf_NUTS, resource_class)



    ##### Fix params_local
    if params_local['vmin']=='':
        params_local['vmin'] = gdf[feature].min()

    if params_local['vmax']=='':
        params_local['vmax'] = gdf[feature].max()
    
    
    
    ##### Plot in map
    gdf.plot(ax=ax, column=feature, 
             cmap=params['cmap'], edgecolor=params['edgecolor'], lw=params['lw'],
             vmin=params_local['vmin'], vmax=params_local['vmax'], 
             legend=True)


    if feature=='area_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'Area. Total: {total:.2f} km2')

    if feature=='p_nom_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Installed capacity. Total: {total:.2f} MW')        

    if feature=='p_nom_density_NUTS':
        ax.set_title(f'{carrier} : Installed capacity density [MW/km2]')

    if feature=='p_nom_max_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Potential. Total: {total:.2f} MW')    

    if feature=='p_nom_max_density_NUTS':
        ax.set_title(f'{carrier} : Potential density [MW/km2]')                    

    if feature=='p_nom_max_ratio_NUTS':
        ax.set_title(f'{carrier} : ratio installed capacity / potential')                

    if feature=='p_nom_opt_NUTS':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Optimal capacity. Total: {total:.2f} MW')  

    if feature=='p_nom_opt_density_NUTS':
        ax.set_title(f'{carrier} : Optimal capacity density [MW/km2]')                      

    if feature=='p_nom_opt_max_ratio_NUTS':
        ax.set_title(f'{carrier} : ratio optimal capacity / potential') 

