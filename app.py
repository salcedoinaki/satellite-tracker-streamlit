import streamlit as st
st.set_page_config(layout="wide")  # Use a wide layout

import importlib
import requests

# Import other dependencies
from satellite import get_satellite_path_with_edges
from scheduler import greedy_schedule
from visualizer import plot_multiple_satellites
from target_list import TARGETS as DEFAULT_TARGETS

# ------------------------------------------------
# Import streamlit-geolocation using importlib
# ------------------------------------------------
try:
    st_geo = importlib.import_module("streamlit_geolocation")
except Exception as e:
    st.error("Failed to import streamlit_geolocation: " + str(e))
    st.stop()

# ------------------------------------------------
# Application Title & Description
# ------------------------------------------------
st.title("Optimus2: Satellite Mission Planner")
st.markdown(
    """
This application simulates satellites’ ground tracks based on TLE data, calculates their swath edges, 
and determines which ground targets are captured during their passes.
    """
)

# ------------------------------------------------
# Initialize Session State Variables
# ------------------------------------------------
if "satellites" not in st.session_state:
    st.session_state.satellites = []
if "custom_targets" not in st.session_state:
    st.session_state.custom_targets = []
if "simulation_run" not in st.session_state:
    st.session_state.simulation_run = False
if "sidebar_hidden" not in st.session_state:
    st.session_state.sidebar_hidden = False
if "my_location" not in st.session_state:
    st.session_state.my_location = None

# ------------------------------------------------
# Sidebar: Satellite Inputs & TLE Loader
# ------------------------------------------------
st.sidebar.header("Satellite Inputs")

# Manual Satellite Addition (defaulting to an example satellite)
default_name_49 = "NUSAT-49 (K.VON NEUMANN)"
default_tle1_49 = "1 60500U 24149AJ  25062.80085819  .00012619  00000-0  51125-3 0  9991"
default_tle2_49 = "2 60500  97.4170 141.8271 0005273 137.7873 222.3772 15.24786286 30252"

sat_name_input = st.sidebar.text_input("Satellite Name", value=default_name_49, key="sat_name_input")
sat_tle1_input = st.sidebar.text_area("TLE Line 1", value=default_tle1_49, height=80, key="sat_tle1_input")
sat_tle2_input = st.sidebar.text_area("TLE Line 2", value=default_tle2_49, height=80, key="sat_tle2_input")
if st.sidebar.button("Add Satellite", key="add_satellite"):
    st.session_state.satellites.append({
        "name": sat_name_input,
        "tle1": sat_tle1_input,
        "tle2": sat_tle2_input
    })
    st.sidebar.success(f"Added satellite: {sat_name_input}")

# Automated TLE Loader Section
st.sidebar.header("Automated TLE Loader")
TLE_SOURCES = {
    "Planet Labs": "https://celestrak.com/NORAD/elements/planet-labs-doves.txt",
    "Maxar": "https://celestrak.com/NORAD/elements/maxar.txt",   # placeholder URL
    "Spire": "https://celestrak.com/NORAD/elements/spire.txt",     # placeholder URL
    "BlackSky": "https://celestrak.com/NORAD/elements/blacksky.txt"  # placeholder URL
}
selected_constellation = st.sidebar.selectbox("Select Constellation", list(TLE_SOURCES.keys()), key="constellation_select")
if st.sidebar.button("Load TLEs for " + selected_constellation, key="load_tle"):
    def fetch_tle_from_url(url):
        response = requests.get(url)
        if response.status_code == 200:
            lines = response.text.strip().splitlines()
            satellites = []
            # Assume TLE file is in groups of 3 lines: name, TLE line 1, TLE line 2
            for i in range(0, len(lines), 3):
                if i + 2 < len(lines):
                    name = lines[i].strip()
                    tle1 = lines[i+1].strip()
                    tle2 = lines[i+2].strip()
                    satellites.append({"name": name, "tle1": tle1, "tle2": tle2})
            return satellites
        else:
            return []
    fetched_satellites = fetch_tle_from_url(TLE_SOURCES[selected_constellation])
    if fetched_satellites:
        st.session_state.satellites.extend(fetched_satellites)
        st.sidebar.success(f"Loaded {len(fetched_satellites)} satellites from {selected_constellation}")
    else:
        st.sidebar.error("Failed to load TLEs for " + selected_constellation)

# Display current satellites and a button to clear them
if st.session_state.satellites:
    st.sidebar.markdown("### Added Satellites:")
    for idx, sat in enumerate(st.session_state.satellites, start=1):
        st.sidebar.write(f"{idx}. {sat['name']}")
    if st.sidebar.button("Clear Satellites", key="clear_satellites"):
        st.session_state.satellites = []

# If no satellites are added manually or via loader, load default satellites
if not st.session_state.satellites:
    st.session_state.satellites.extend([
        {"name": "NUSAT-49 (K.VON NEUMANN)", "tle1": default_tle1_49, "tle2": default_tle2_49},
        {"name": "NUSAT-48 (H. LEAVITT)", "tle1": "1 60498U 24149AG  25063.19715943  .00012207  00000-0  49433-3 0  9990", "tle2": "2 60498  97.4141 142.1370 0006190 141.9860 218.1815 15.24803829 30313"},
        {"name": "NUSAT-43 (R DIENG-KUNTZ)", "tle1": "1 56968U 23084AN  25062.90489487  .00027461  00000-0  75956-3 0  9990", "tle2": "2 56968  97.4056 188.3598 0008506 140.2478 219.9391 15.36949714 96091"},
        {"name": "NUSAT-37 (JOAN CLARKE)", "tle1": "1 56203U 23054AB  25063.13797017  .00034586  00000-0  79821-3 0  9997", "tle2": "2 56203  97.3024 323.8645 0003920 307.3420  52.7470 15.42466052106071"},
        {"name": "NUSAT-32 (ALBANIA-1)", "tle1": "1 55064U 23001BH  25063.16250878  .00033724  00000-0  76753-3 0  9999", "tle2": "2 55064  97.2483 124.9603 0005931 306.6957  53.3746 15.42878823121026"},
        {"name": "NUSAT-29 (EDITH CLARKE)", "tle1": "1 52764U 22057AJ  25063.25002839  .00046176  00000-0  97283-3 0  9991", "tle2": "2 52764  97.4726 191.4589 0006861 191.1837 168.9261 15.45099026154632"}
    ])

# ------------------------------------------------
# Sidebar: Simulation Parameters
# ------------------------------------------------
st.sidebar.header("Simulation Parameters")
duration_minutes = st.sidebar.number_input("Duration (minutes)", min_value=10, max_value=240, value=240, step=10, key="duration")
step_seconds = st.sidebar.number_input("Time Step (seconds)", min_value=10, max_value=600, value=60, step=10, key="step_seconds")
swath_radius_km = st.sidebar.number_input("Swath Radius (km)", min_value=10, max_value=200, value=75, step=5, key="swath_radius")

# ------------------------------------------------
# Sidebar: Custom Target Input
# ------------------------------------------------
st.sidebar.header("Custom Target Input")
target_lat = st.sidebar.number_input("Target Latitude", value=0.0, format="%.4f", key="target_lat")
target_lon = st.sidebar.number_input("Target Longitude", value=0.0, format="%.4f", key="target_lon")
if st.sidebar.button("Add Target", key="add_target"):
    st.session_state.custom_targets.append((target_lat, target_lon))
    st.sidebar.success(f"Added target: ({target_lat}, {target_lon})")

# ------------------------------------------------
# Sidebar: Geolocation Section (Auto Request Location)
# ------------------------------------------------
st.sidebar.header("Get My Location (via Browser)")

# Use the attribute "streamlit_geolocation" from st_geo (based on debug output)
if hasattr(st_geo, "streamlit_geolocation"):
    geolocation_function = st_geo.streamlit_geolocation
else:
    geolocation_function = None
    st.sidebar.error("No geolocation function found in streamlit_geolocation module.")

# Automatically request location if not already obtained
if geolocation_function and st.session_state.my_location is None:
    try:
        coords = geolocation_function()
        st.session_state.my_location = coords
    except Exception as e:
        st.session_state.my_location = None

if st.session_state.my_location:
    coords = st.session_state.my_location
    lat = coords.get("latitude")
    lon = coords.get("longitude")
    if lat is not None and lon is not None:
        st.sidebar.write("Your Location:")
        st.sidebar.write(f"Latitude: {lat:.4f}")
        st.sidebar.write(f"Longitude: {lon:.4f}")
        if st.sidebar.button("Add My Location to Targets", key="add_location"):
            st.session_state.custom_targets.append((lat, lon))
            st.sidebar.success("Location added to targets!")
    else:
        st.sidebar.warning("Location data is not available. Check browser permissions.")
else:
    st.sidebar.warning("Location not available.")

if st.session_state.custom_targets:
    st.sidebar.markdown("### Custom Targets:")
    for idx, target in enumerate(st.session_state.custom_targets, start=1):
        st.sidebar.write(f"{idx}. ({target[0]}, {target[1]})")
    if st.sidebar.button("Clear Custom Targets", key="clear_targets"):
        st.session_state.custom_targets = []

# Use custom targets if provided; otherwise, use the default target list
if st.session_state.custom_targets:
    targets = st.session_state.custom_targets
else:
    targets = DEFAULT_TARGETS

# ------------------------------------------------
# Sidebar: Run Simulation Button
# ------------------------------------------------
if st.sidebar.button("Run Simulation", key="run_simulation"):
    st.session_state.simulation_run = True
    st.session_state.sidebar_hidden = True

# ------------------------------------------------
# Toggle Sidebar Visibility Buttons (Main Page)
# ------------------------------------------------
if st.session_state.sidebar_hidden:
    if st.button("Show Sidebar", key="show_sidebar"):
        st.session_state.sidebar_hidden = False
        try:
            st.experimental_rerun()
        except Exception:
            st.warning("Please refresh the page manually to show the sidebar.")
else:
    if st.button("Hide Sidebar", key="hide_sidebar"):
        st.session_state.sidebar_hidden = True
        try:
            st.experimental_rerun()
        except Exception:
            st.warning("Please refresh the page manually to hide the sidebar.")

if st.session_state.sidebar_hidden:
    hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# ------------------------------------------------
# Run Simulation and Display Output
# ------------------------------------------------
if st.session_state.get("simulation_run", False):
    st.write("Running simulation...")
    sat_data_list = []
    captured_info = []
    try:
        for sat in st.session_state.satellites:
            path, left_edge, right_edge = get_satellite_path_with_edges(
                sat["tle1"],
                sat["tle2"],
                sat["name"],
                duration_minutes,
                step_seconds,
                swath_radius_km
            )
            captured = greedy_schedule(path, targets, swath_radius_km)
            captured_info.append({
                "name": sat["name"],
                "captured": captured
            })
            sat_data_list.append({
                "name": sat["name"],
                "path": path,
                "left_edge": left_edge,
                "right_edge": right_edge,
                "captured": captured
            })
        fig = plot_multiple_satellites(sat_data_list, targets)
        st.pyplot(fig)
        st.write("### Captured Targets:")
        for info in captured_info:
            st.write(f"**{info['name']}**:")
            if info["captured"]:
                for cap in info["captured"]:
                    st.write(f"Target at {cap['target']} captured at {cap['time']}")
            else:
                st.write("No targets captured during this pass.")
    except Exception as e:
        st.error(f"Error during simulation: {e}")
