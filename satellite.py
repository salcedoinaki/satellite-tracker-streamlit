# satellite.py
from skyfield.api import load, EarthSatellite
import numpy as np

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
    # Calculate time steps
    steps = int(duration_minutes * 60 / step_seconds)
    t0 = ts.now()
    # Create an array of time steps
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
