import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json
import os
import uuid
from geopy.distance import geodesic
import base64
from io import BytesIO

# Set page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Station Location Recorder",
    page_icon="📍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .location-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #1E3A8A;
        margin: 20px 0;
        text-align: center;
    }
    .stButton > button {
        background-color: #1E3A8A;
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 15px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 15px 0;
    }
    .instructions {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing locations
if 'locations' not in st.session_state:
    st.session_state.locations = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if 'station_name' not in st.session_state:
    st.session_state.station_name = ""

# Define target stations with their coordinates (example data - you should update these)
STATIONS = {
    "Central Station": {"lat": 40.7128, "lon": -74.0060},
    "North Terminal": {"lat": 40.7589, "lon": -73.9851},
    "West Depot": {"lat": 40.7489, "lon": -73.9680},
    "South Hub": {"lat": 40.7549, "lon": -73.9840},
    "East Station": {"lat": 40.7505, "lon": -73.9934}
}

# Function to calculate distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters

# Function to find nearest station
def find_nearest_station(user_lat, user_lon):
    nearest_station = None
    min_distance = float('inf')
    
    for station_name, coords in STATIONS.items():
        distance = calculate_distance(user_lat, user_lon, coords["lat"], coords["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest_station = station_name
    
    return nearest_station, min_distance

# Function to create download link
def get_download_link(df, filename="station_locations.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="background-color: #1E3A8A; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Download CSV</a>'
    return href

# Main app layout
st.markdown('<div class="main-header">📍 Station Location Recorder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automatically record latitude and longitude when users access this link</div>', unsafe_allow_html=True)

# Instructions
with st.expander("📋 How to use this app", expanded=True):
    st.markdown("""
    ### Instructions for Administrators:
    1. **Share this link** with people at your stations
    2. When they click the link, their device will ask for location permission
    3. Their coordinates will be automatically recorded with timestamp
    4. **Download the collected data** as CSV for analysis
    
    ### For Users (People at Stations):
    1. Click "Allow" when your browser asks for location permission
    2. Wait for the confirmation message
    3. That's it! Your station location has been recorded
    """)

# Main interface
tab1, tab2, tab3 = st.tabs(["📍 Record Location", "📊 View Data", "⚙️ Admin Settings"])

with tab1:
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.write("### Get Your Current Location")
    st.write("Click the button below to record your location. Make sure you're at the station!")
    
    # Location capture button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        get_location = st.button("📍 RECORD MY LOCATION", key="get_loc")
    
    if get_location:
        try:
            # JavaScript to get geolocation
            geolocation_js = """
            <script>
            function getLocation() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        function(position) {
                            // Send data back to Streamlit
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                value: position.coords.latitude + ',' + position.coords.longitude
                            }, '*');
                        },
                        function(error) {
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                value: 'error:' + error.message
                            }, '*');
                        },
                        {enableHighAccuracy: true, timeout: 10000, maximumAge: 0}
                    );
                } else {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: 'error:Geolocation not supported'
                    }, '*');
                }
            }
            getLocation();
            </script>
            """
            
            # Display the JavaScript
            components.html(geolocation_js, height=0)
            
            # Create a text input to receive the location data
            location_data = st.text_input("Location data will appear here", key="loc_input", label_visibility="collapsed")
            
            if location_data and 'error' not in location_data:
                try:
                    lat, lon = map(float, location_data.split(','))
                    
                    # Get current timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Find nearest station
                    nearest_station, distance = find_nearest_station(lat, lon)
                    
                    # Store in session state
                    location_record = {
                        "session_id": st.session_state.session_id,
                        "timestamp": timestamp,
                        "latitude": lat,
                        "longitude": lon,
                        "nearest_station": nearest_station,
                        "distance_meters": round(distance, 2),
                        "station_name": st.session_state.station_name if st.session_state.station_name else "Unknown"
                    }
                    
                    st.session_state.locations.append(location_record)
                    
                    # Display success message
                    st.markdown(f"""
                    <div class="success-box">
                    <h4>✅ Location Recorded Successfully!</h4>
                    <p><strong>Time:</strong> {timestamp}</p>
                    <p><strong>Coordinates:</strong> {lat:.6f}, {lon:.6f}</p>
                    <p><strong>Nearest Station:</strong> {nearest_station}</p>
                    <p><strong>Distance:</strong> {distance:.1f} meters</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Auto-refresh to show updated data
                    time.sleep(2)
                    st.rerun()
                    
                except ValueError:
                    st.error("Invalid location data received")
            
            elif 'error' in location_data:
                st.error(f"Location error: {location_data.split(':')[1]}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("If location is not working, try using Chrome or Edge browser with HTTPS")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.write("## 📊 Collected Location Data")
    
    if len(st.session_state.locations) > 0:
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.locations)
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Unique Sessions", df['session_id'].nunique())
        with col3:
            st.metric("Stations Covered", df['nearest_station'].nunique())
        with col4:
            if not df.empty:
                st.metric("Latest", df.iloc[-1]['timestamp'].split()[0])
        
        # Display data table
        st.dataframe(df, use_container_width=True)
        
        # Download button
        st.markdown(get_download_link(df), unsafe_allow_html=True)
        
        # Show on map
        st.write("### 📍 Locations Map")
        if not df.empty:
            # Create a simple map display
            map_data = df[['latitude', 'longitude']].copy()
            map_data.columns = ['lat', 'lon']
            st.map(map_data, zoom=12)
    else:
        st.info("No location data recorded yet. Share the link with station visitors!")

with tab3:
    st.write("## ⚙️ Admin Settings")
    
    # Station selection
    st.write("### Station Configuration")
    selected_station = st.selectbox(
        "Select Station (for manual entry)",
        ["Select a station"] + list(STATIONS.keys())
    )
    
    if selected_station != "Select a station":
        st.session_state.station_name = selected_station
        st.success(f"Station set to: {selected_station}")
        st.write(f"Coordinates: {STATIONS[selected_station]['lat']}, {STATIONS[selected_station]['lon']}")
    
    # Manual location entry (for testing)
    st.write("### Manual Location Entry (For Testing)")
    with st.form("manual_entry"):
        col1, col2 = st.columns(2)
        with col1:
            manual_lat = st.number_input("Latitude", value=40.7128, format="%.6f")
        with col2:
            manual_lon = st.number_input("Longitude", value=-74.0060, format="%.6f")
        
        station_for_manual = st.selectbox("Station Name", list(STATIONS.keys()))
        
        if st.form_submit_button("Add Manual Entry"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            distance = calculate_distance(manual_lat, manual_lon, 
                                         STATIONS[station_for_manual]["lat"], 
                                         STATIONS[station_for_manual]["lon"])
            
            location_record = {
                "session_id": "manual_" + str(uuid.uuid4())[:8],
                "timestamp": timestamp,
                "latitude": manual_lat,
                "longitude": manual_lon,
                "nearest_station": station_for_manual,
                "distance_meters": round(distance, 2),
                "station_name": station_for_manual
            }
            
            st.session_state.locations.append(location_record)
            st.success("Manual entry added!")
            st.rerun()
    
    # Clear data option
    st.write("### Data Management")
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.locations = []
        st.success("All data cleared!")
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📍 Station Location Recorder | Automatically records device GPS coordinates | "
    f"Session ID: {st.session_state.session_id}"
    "</div>",
    unsafe_allow_html=True
)

# Add JavaScript for geolocation
components.html("""
<script>
// Listen for geolocation messages
window.addEventListener('message', function(event) {
    if (event.data.type === 'streamlit:setComponentValue') {
        // This would be handled by Streamlit's component system
        console.log('Location received:', event.data.value);
    }
});
</script>
""", height=0)
