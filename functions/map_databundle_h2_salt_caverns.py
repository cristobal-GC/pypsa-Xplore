

import cartopy
import matplotlib



def map_databundle_h2_salt_caverns(ax,h2_salt_caverns, limit_spain):
    '''
    This function is to include h2 salt caverns with a representative key:
    '''
    


    #fig, ax= plt.subplots(figsize=(9,7))
    custom_colors = matplotlib.colors.ListedColormap(["#4a3b8e", "#7ab595", "#e3f68d", "#efdc80", "#c75f3c", "#730d35"])
    #NUTS0.plot(ax=ax, color="grey", edgecolor="grey", linewidth=0.4, alpha=0.4)
    h2_salt_caverns.plot(ax=ax, column="val_kwhm3", 
                     legend=True, 
                     categorical=True, 
                     cmap=custom_colors,
                     legend_kwds={"frameon":False, "bbox_to_anchor":(1.22, 0.7), "title":"Energy Density\n[kWh/m³]"})
    #We limit the map to the h2 cavern map extent 
    lim_h2=h2_salt_caverns.total_bounds
    buffer=1.7
    if limit_spain==True:
        ax.set_xlim(-10,4.5)
        ax.set_ylim(35, 44.5)
    else:
        ax.set_xlim(lim_h2[0]-buffer,lim_h2[2]+buffer)
        ax.set_ylim(lim_h2[1]-buffer, lim_h2[3]+buffer)

    ax.set_ylabel("Latitude")
    ax.set_xlabel("Longitude")
