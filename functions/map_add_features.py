

import cartopy



def map_add_features(ax, params):
    '''
    This function is to include features in a map:
    - borders
    - coastlines
    - land color
    - ocean color

    params['scale'] sets the Natural Earth resolution ('10m', '50m' or '110m').
    Cartopy's default is '110m', which is too coarse for regional maps and
    shifts coastlines and borders by tens of km with respect to the data.
    '''

    scale = params.get('scale', '10m')

    ax.add_feature(cartopy.feature.BORDERS.with_scale(scale), color=params['color_BORDERS'], linewidth=params['linewidth'])
    ax.add_feature(cartopy.feature.COASTLINE.with_scale(scale), color=params['color_COASTLINE'], linewidth=params['linewidth'])
    ax.add_feature(cartopy.feature.LAND.with_scale(scale), edgecolor='none', facecolor=params['color_LAND'])
    ax.add_feature(cartopy.feature.OCEAN.with_scale(scale), edgecolor='none', facecolor=params['color_OCEAN'])
