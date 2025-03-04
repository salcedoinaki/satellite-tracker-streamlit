# scheduler.py
from geopy.distance import great_circle

def greedy_schedule(path, targets, swath_radius_km=75):
    """
    Determines which targets are captured by the satellite.
    
    Args:
        path (List[dict]): Satellite path with keys 'lat' and 'lon'.
        targets (List[tuple]): List of target coordinates as (lat, lon).
        swath_radius_km (float): Radius within which a target is considered captured.
        
    Returns:
        List[dict]: Each dict contains 'target' (the target coordinate) and 'time' (capture time).
    """
    captured = []
    # Make a copy so we can remove captured ones
    remaining_targets = targets.copy()
    
    for point in path:
        point_coords = (point['lat'], point['lon'])
        for target in remaining_targets:
            distance = great_circle(point_coords, target).km
            if distance <= swath_radius_km:
                captured.append({'target': target, 'time': point['time']})
        # Remove already captured targets
        remaining_targets = [t for t in remaining_targets if t not in [cap['target'] for cap in captured]]
        if not remaining_targets:
            break
    return captured
