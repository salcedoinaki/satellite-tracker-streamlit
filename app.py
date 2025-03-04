# app.py (Satellite Input Section updated)
import streamlit as st
from satellite import get_satellite_path_with_edges
from scheduler import greedy_schedule
from visualizer import plot_multiple_satellites
from target_list import TARGETS as DEFAULT_TARGETS

st.title("Optimus2: Satellite Mission Planner")

st.markdown("""
This application simulates satellites’ ground tracks based on TLE data, calculates their swath edges, and determines which ground targets are captured during their passes.
""")

# -------------------------------
# Satellite Input Section
# -------------------------------
st.sidebar.header("Satellite Inputs")

if 'satellites' not in st.session_state:
    st.session_state.satellites = []

# --- Old Default Satellites ---
# NUSAT-49 (K.VON NEUMANN)
default_name_49 = "NUSAT-49 (K.VON NEUMANN)"
default_tle1_49 = "1 60500U 24149AJ  25062.80085819  .00012619  00000-0  51125-3 0  9991"
default_tle2_49 = "2 60500  97.4170 141.8271 0005273 137.7873 222.3772 15.24786286 30252"

# NUSAT-48 (H. LEAVITT)
default_name_48 = "NUSAT-44 MARIA MITCHELL"
default_tle1_48 = "1 59122U 24043AA  25063.11266256  .00019752  00000-0  66335-3 0  9997"
default_tle2_48 = "2 59122  97.4992 192.9560 0011001  97.2269 263.0223 15.30832405 55415"


# --- New Default Satellogic Satellites from satcat.com ---
# NUSAT-43 (R DIENG-KUNTZ)
default_name_43 = "NUSAT-43 (R DIENG-KUNTZ)"
default_tle1_43 = "1 56968U 23084AN  25062.90489487  .00027461  00000-0  75956-3 0  9990"
default_tle2_43 = "2 56968  97.4056 188.3598 0008506 140.2478 219.9391 15.36949714 96091"

# NUSAT-37 (JOAN CLARKE)
default_name_37 = "NUSAT-37 (JOAN CLARKE)"
default_tle1_37 = "1 56203U 23054AB  25063.13797017  .00034586  00000-0  79821-3 0  9997"
default_tle2_37 = "2 56203  97.3024 323.8645 0003920 307.3420  52.7470 15.42466052106071"

# NUSAT-32 (ALBANIA-1)
default_name_32 = "NUSAT-32 (ALBANIA-1)"
default_tle1_32 = "1 55064U 23001BH  25063.16250878  .00033724  00000-0  76753-3 0  9999"
default_tle2_32 = "2 55064  97.2483 124.9603 0005931 306.6957  53.3746 15.42878823121026"

# NUSAT-29 (EDITH CLARKE)
default_name_29 = "NUSAT-29 (EDITH CLARKE)"
default_tle1_29 = "1 52764U 22057AJ  25063.25002839  .00046176  00000-0  97283-3 0  9991"
default_tle2_29 = "2 52764  97.4726 191.4589 0006861 191.1837 168.9261 15.45099026154632"

# Input fields for a new satellite (defaulting to NUSAT-49 for convenience)
sat_name_input = st.sidebar.text_input("Satellite Name", value=default_name_49, key="sat_name")
sat_tle1_input = st.sidebar.text_area("TLE Line 1", value=default_tle1_49, height=80, key="sat_tle1")
sat_tle2_input = st.sidebar.text_area("TLE Line 2", value=default_tle2_49, height=80, key="sat_tle2")
if st.sidebar.button("Add Satellite"):
    st.session_state.satellites.append({
        "name": sat_name_input,
        "tle1": sat_tle1_input,
        "tle2": sat_tle2_input
    })
    st.sidebar.success(f"Added satellite: {sat_name_input}")

# Display added satellites with an option to clear them
if st.session_state.satellites:
    st.sidebar.markdown("### Added Satellites:")
    for idx, sat in enumerate(st.session_state.satellites, start=1):
        st.sidebar.write(f"{idx}. {sat['name']}")
    if st.sidebar.button("Clear Satellites"):
        st.session_state.satellites = []

# If no satellites are manually added, use all default satellites
if not st.session_state.satellites:
    st.session_state.satellites.extend([
        {"name": default_name_49, "tle1": default_tle1_49, "tle2": default_tle2_49},
        {"name": default_name_48, "tle1": default_tle1_48, "tle2": default_tle2_48},
        {"name": default_name_43, "tle1": default_tle1_43, "tle2": default_tle2_43},
        {"name": default_name_37, "tle1": default_tle1_37, "tle2": default_tle2_37},
        {"name": default_name_32, "tle1": default_tle1_32, "tle2": default_tle2_32},
        {"name": default_name_29, "tle1": default_tle1_29, "tle2": default_tle2_29}
    ])

# -------------------------------
# Simulation Parameters
# -------------------------------
st.sidebar.header("Simulation Parameters")
duration_minutes = st.sidebar.number_input("Duration (minutes)", min_value=10, max_value=240, value=240, step=10)
step_seconds = st.sidebar.number_input("Time Step (seconds)", min_value=10, max_value=600, value=60, step=10)
swath_radius_km = st.sidebar.number_input("Swath Radius (km)", min_value=10, max_value=200, value=75, step=5)

# -------------------------------
# Target Input Section
# -------------------------------
st.sidebar.header("Custom Target Input")
if 'custom_targets' not in st.session_state:
    st.session_state.custom_targets = []

target_lat = st.sidebar.number_input("Target Latitude", value=0.0, format="%.4f", key="target_lat")
target_lon = st.sidebar.number_input("Target Longitude", value=0.0, format="%.4f", key="target_lon")
if st.sidebar.button("Add Target"):
    st.session_state.custom_targets.append((target_lat, target_lon))
    st.sidebar.success(f"Added target: ({target_lat}, {target_lon})")

if st.session_state.custom_targets:
    st.sidebar.markdown("### Custom Targets:")
    for idx, target in enumerate(st.session_state.custom_targets, start=1):
        st.sidebar.write(f"{idx}. ({target[0]}, {target[1]})")
    if st.sidebar.button("Clear Custom Targets"):
        st.session_state.custom_targets = []

# Use custom targets if provided, else use default target list
if st.session_state.custom_targets:
    targets = st.session_state.custom_targets
else:
    targets = DEFAULT_TARGETS

# -------------------------------
# Run Simulation
# -------------------------------
if st.sidebar.button("Run Simulation"):
    st.write("Running simulation...")
    sat_data_list = []  # To collect each satellite's simulation data
    captured_info = []  # To collect captured target info per satellite
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
            # Determine captured targets for this satellite
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
            
        # Generate and display the combined plot for all satellites
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
