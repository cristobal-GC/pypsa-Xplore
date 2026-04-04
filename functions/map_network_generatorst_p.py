

from .gdf_network_generatorst_p import gdf_network_generatorst_p



def map_network_generatorst_p(carrier, n, feature, ax, gdf_regions, resource_class, params, params_local):
    """
    This function plots generation_t features based on p (after dispatch) for a specific carrier
    in the geometry of a network.

    Features:
      - AEP                 : Annual Energy Production [TWh]  
    """

    gdf = gdf_network_generatorst_p(carrier, n, gdf_regions, resource_class)



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


    if feature=='AEP':
        total = gdf[feature].sum()
        ax.set_title(f'{carrier} : Annual Energy Production. Total: {total:.2f} TWh')

