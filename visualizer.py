# visualizer.py
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_satellite_path(path, targets, captured_targets):
    """
    Plots the satellite path, all targets, and captured targets on a world map using Cartopy.
    
    Args:
        path (List[dict]): Satellite path with keys 'lat' and 'lon'.
        targets (List[tuple]): List of target coordinates.
        captured_targets (List[dict]): Captured targets with 'target' key.
    
    Returns:
        matplotlib.figure.Figure: The generated plot.
    """
    # Create a figure with the PlateCarree projection (suitable for world maps)
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Add map features: coastlines, borders, land, and ocean colors
    ax.set_global()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    
    # Plot the satellite path
    lats = [point['lat'] for point in path]
    lons = [point['lon'] for point in path]
    ax.plot(lons, lats, label='Satellite Path', color='blue', transform=ccrs.Geodetic())
    
    # Plot all targets
    t_lats = [t[0] for t in targets]
    t_lons = [t[1] for t in targets]
    ax.scatter(t_lons, t_lats, label='Targets', color='green', marker='o', transform=ccrs.Geodetic())
    
    # Plot captured targets if any
    if captured_targets:
        c_lats = [ct['target'][0] for ct in captured_targets]
        c_lons = [ct['target'][1] for ct in captured_targets]
        ax.scatter(c_lons, c_lats, label='Captured Targets', color='gold', marker='*', s=150, transform=ccrs.Geodetic())
    
    ax.set_title('Satellite Ground Track and Target Capture')
    ax.legend()
    return fig
