

from .gdf_network_generatorst_pmaxpu import gdf_network_generatorst_pmaxpu



def map_network_generatorst_pmaxpu(carrier, n, feature, ax, gdf_regions, params, params_local, gen_class=0):
    """
    This function plots generation_t features based on p_max_pu for a specific carrier
    in the geometry of a network.

    Features:
      - CF					: Annual capacity factor [-]  
    """

    gdf = gdf_network_generatorst_pmaxpu(carrier, n, gdf_regions, gen_class)



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


    if feature=='CF':
        ax.set_title(f'{carrier} : CF')

