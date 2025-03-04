# app.py
import streamlit as st
from satellite import get_satellite_path
from scheduler import greedy_schedule
from visualizer import plot_satellite_path
from target_list import TARGETS as DEFAULT_TARGETS

st.title("Optimus2: Satellite Mission Planner")

st.markdown("""
This application simulates a satellite’s ground track based on TLE data and determines which ground targets are captured during its pass.
""")

# Sidebar for simulation parameters
st.sidebar.header("Simulation Parameters")

# Default TLE for the ISS (ZARYA) as an example
default_name = "ISS (ZARYA)"
default_tle1 = "1 25544U 98067A   20330.54791667  .00002182  00000-0  44552-4 0  9992"
default_tle2 = "2 25544  51.6449 197.1028 0001289  72.3040  56.2194 15.49125134256117"

satellite_name = st.sidebar.text_input("Satellite Name", value=default_name)
tle_line1 = st.sidebar.text_area("TLE Line 1", value=default_tle1, height=100)
tle_line2 = st.sidebar.text_area("TLE Line 2", value=default_tle2, height=100)

duration_minutes = st.sidebar.number_input("Duration (minutes)", min_value=10, max_value=240, value=90, step=10)
step_seconds = st.sidebar.number_input("Time Step (seconds)", min_value=10, max_value=600, value=60, step=10)
swath_radius_km = st.sidebar.number_input("Swath Radius (km)", min_value=10, max_value=200, value=75, step=5)

# Sidebar for target input
st.sidebar.header("Custom Target Input")

# Initialize session state to store custom targets
if 'custom_targets' not in st.session_state:
    st.session_state.custom_targets = []

# Input fields for custom target coordinates
target_lat = st.sidebar.number_input("Target Latitude", value=0.0, format="%.4f")
target_lon = st.sidebar.number_input("Target Longitude", value=0.0, format="%.4f")
if st.sidebar.button("Add Target"):
    st.session_state.custom_targets.append((target_lat, target_lon))
    st.sidebar.success(f"Added target: ({target_lat}, {target_lon})")

# Display current custom targets
if st.session_state.custom_targets:
    st.sidebar.markdown("### Custom Targets:")
    for idx, target in enumerate(st.session_state.custom_targets, start=1):
        st.sidebar.write(f"{idx}. ({target[0]}, {target[1]})")
        
    if st.sidebar.button("Clear Custom Targets"):
        st.session_state.custom_targets = []

# Decide which target list to use: custom targets take precedence
if st.session_state.custom_targets:
    targets = st.session_state.custom_targets
else:
    targets = DEFAULT_TARGETS

if st.sidebar.button("Run Simulation"):
    st.write("Running simulation...")
    try:
        # Compute the satellite path based on TLE data and parameters
        path = get_satellite_path(tle_line1, tle_line2, satellite_name, duration_minutes, step_seconds)
        # Determine which targets are captured
        captured = greedy_schedule(path, targets, swath_radius_km)
        # Generate and display the plot
        fig = plot_satellite_path(path, targets, captured)
        st.pyplot(fig)
        
        st.write("### Captured Targets:")
        if captured:
            for cap in captured:
                st.write(f"Target at {cap['target']} captured at time {cap['time']}")
        else:
            st.write("No targets captured during this pass.")
    except Exception as e:
        st.error(f"Error during simulation: {e}")
