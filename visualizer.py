# visualizer.py
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_multiple_satellites(sat_data_list, targets):
    """
    Plots multiple satellites' ground tracks along with their swath edges on a world map.
    
    Args:
        sat_data_list (List[dict]): Each dict should contain:
            - 'name': Satellite name
            - 'path': List of dicts with 'lat' and 'lon'
            - 'left_edge': List of dicts with 'lat' and 'lon'
            - 'right_edge': List of dicts with 'lat' and 'lon'
            - 'captured': List of capture events (each a dict)
        targets (List[tuple]): List of target coordinates (lat, lon)
    
    Returns:
        matplotlib.figure.Figure: The generated plot.
    """
    fig, ax = plt.subplots(figsize=(18, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    
    ax.set_global()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    
    colors = ['blue', 'green', 'purple', 'brown', 'cyan', 'magenta']
    
    for i, sat in enumerate(sat_data_list):
        color = colors[i % len(colors)]
        # Plot center path (to be included in the legend)
        lats = [p['lat'] for p in sat['path']]
        lons = [p['lon'] for p in sat['path']]
        ax.plot(lons, lats, label=f"{sat['name']} Path", color=color, transform=ccrs.Geodetic())
        
        # Plot left and right edges (no legend labels)
        lats_left = [p['lat'] for p in sat['left_edge']]
        lons_left = [p['lon'] for p in sat['left_edge']]
        ax.plot(lons_left, lats_left, color=color, linestyle='--', transform=ccrs.Geodetic())
        
        lats_right = [p['lat'] for p in sat['right_edge']]
        lons_right = [p['lon'] for p in sat['right_edge']]
        ax.plot(lons_right, lats_right, color=color, linestyle='-.', transform=ccrs.Geodetic())
    
    # Plot targets
    t_lats = [t[0] for t in targets]
    t_lons = [t[1] for t in targets]
    ax.scatter(t_lons, t_lats, label='Targets', color='black', marker='o', transform=ccrs.Geodetic())
    
    ax.set_title('Satellite Ground Tracks with Swath Edges and Target Capture')
    # Move the legend below the plot
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    return fig