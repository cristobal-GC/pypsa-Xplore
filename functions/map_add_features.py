

import cartopy



def map_add_features(ax, params):
    '''
    This function is to include features in a map:
    - borders
    - coastlines
    - land color
    - ocean color
    '''

    ax.add_feature(cartopy.feature.BORDERS, color=params['color_BORDERS'], linewidth=params['linewidth'])
    ax.add_feature(cartopy.feature.COASTLINE, color=params['color_COASTLINE'], linewidth=params['linewidth'])
    ax.add_feature(cartopy.feature.LAND,edgecolor='none', facecolor=params['color_LAND'])
    ax.add_feature(cartopy.feature.OCEAN,edgecolor='none', facecolor=params['color_OCEAN'])
