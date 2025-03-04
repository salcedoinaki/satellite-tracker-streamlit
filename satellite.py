# satellite.py
from skyfield.api import load, EarthSatellite
import numpy as np
import math
from geopy.distance import distance as geopy_distance

def get_satellite_path(tle_line1, tle_line2, name, duration_minutes=90, step_seconds=60):
    """
    Returns the satellite ground track for the given TLE.
    
    Args:
        tle_line1 (str): First line of the TLE.
        tle_line2 (str): Second line of the TLE.
        name (str): Satellite name.
        duration_minutes (int): Total simulation duration in minutes.
        step_seconds (int): Time interval in seconds for sampling positions.
        
    Returns:
        List[dict]: Each dict contains 'time', 'lat', and 'lon'.
    """
    ts = load.timescale()
    satellite = EarthSatellite(tle_line1, tle_line2, name, ts)
    steps = int(duration_minutes * 60 / step_seconds)
    t0 = ts.now()
    t_array = ts.utc(
        t0.utc_datetime().year,
        t0.utc_datetime().month,
        t0.utc_datetime().day,
        t0.utc_datetime().hour,
        t0.utc_datetime().minute,
        np.arange(0, duration_minutes * 60, step_seconds)
    )
    
    path = []
    for t in t_array:
        geocentric = satellite.at(t)
        subpoint = geocentric.subpoint()
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        path.append({'time': t.utc_datetime(), 'lat': lat, 'lon': lon})
    return path

def compute_bearing(lat1, lon1, lat2, lon2):
    """
    Compute the bearing in degrees from point A (lat1,lon1) to point B (lat2,lon2)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    diff_long = math.radians(lon2 - lon1)
    x = math.sin(diff_long) * math.cos(lat2_rad)
    y = math.cos(lat1_rad)*math.sin(lat2_rad) - (math.sin(lat1_rad)*math.cos(lat2_rad)*math.cos(diff_long))
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def get_satellite_path_with_edges(tle_line1, tle_line2, name, duration_minutes=90, step_seconds=60, swath_radius_km=75):
    """
    Computes the satellite ground track along with left and right swath edge lines.
    
    Returns:
        tuple: (path, left_edge, right_edge)
            where path is a list of dicts (each with 'time', 'lat', 'lon'),
            left_edge/right_edge are lists of dicts with 'lat' and 'lon'
    """
    path = get_satellite_path(tle_line1, tle_line2, name, duration_minutes, step_seconds)
    left_edge = []
    right_edge = []
    
    for i, point in enumerate(path):
        lat = point['lat']
        lon = point['lon']
        # Use next point to compute bearing if available; else use previous
        if i < len(path) - 1:
            bearing = compute_bearing(lat, lon, path[i+1]['lat'], path[i+1]['lon'])
        else:
            bearing = compute_bearing(path[i-1]['lat'], path[i-1]['lon'], lat, lon)
            
        left_bearing = (bearing - 90) % 360
        right_bearing = (bearing + 90) % 360
        
        left_point = geopy_distance(kilometers=swath_radius_km).destination((lat, lon), left_bearing)
        right_point = geopy_distance(kilometers=swath_radius_km).destination((lat, lon), right_bearing)
        left_edge.append({'lat': left_point.latitude, 'lon': left_point.longitude})
        right_edge.append({'lat': right_point.latitude, 'lon': right_point.longitude})
        
    return path, left_edge, right_edge
