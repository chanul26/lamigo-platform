import pandas as pd
import folium
import sys
import os

# ==========================================
# PATH FIX: Point to root
# ==========================================
# Ensures Python can find the 'simulator' package when running from the root 'ml_core' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simulator import config  # Imports from the local simulator folder

# ==========================================
# 1. DATA INGESTION
# ==========================================
try:
    # We strictly read the read-only 'raw' data. 
    # No random generation happens here, so no random seed is needed.
    df = pd.read_csv("data/raw/customers.csv")
except FileNotFoundError:
    # Updated the error message to reflect the new 'simulator' folder structure
    print("❌ Error: customers.csv not found. Run simulator/00_generate_seed_assets.py first!")
    exit()

# ==========================================
# 2. MAP INITIALIZATION
# ==========================================
# Initialize a Folium map centered roughly on Sri Lanka's West Coast
# 'cartodbpositron' is a clean, light-colored map tile layer that makes our colored markers pop.
m = folium.Map(location=[6.45, 80.05], zoom_start=9, tiles="cartodbpositron")

# ==========================================
# 3. DRAWING THE BOUNDARIES (GEOFENCES)
# ==========================================
# We iterate through the config to draw the physical boundaries of each delivery zone.
for b_id, b_data in config.BRANCH_CONFIGURATIONS.items():
    
    # IMPORTANT GEOMETRY FIX: 
    # Our config.py stores polygons in GeoJSON format: [Longitude, Latitude]
    # But Folium expects coordinates in GPS format: [Latitude, Longitude]
    # We use a list comprehension to swap them on the fly.
    coords = [[p[1], p[0]] for p in b_data["service_area_polygon"]]
    
    # Assign blue to Colombo (B_001) and purple to Galle (B_002)
    poly_color = "blue" if b_id == "B_001" else "purple"
    
    # Draw the translucent service area polygon
    folium.Polygon(
        locations=coords,
        color=poly_color,
        fill=True,
        fill_color=poly_color,
        fill_opacity=0.15,
        popup=f"Service Area: {b_data['facility_name']}"
    ).add_to(m)
    
    # Drop a bold, black "Home" icon right on the warehouse loading dock
    folium.Marker(
        location=[b_data["origin_coordinates"]["latitude"], b_data["origin_coordinates"]["longitude"]],
        popup=f"HUB: {b_data['facility_name']}",
        icon=folium.Icon(color="black", icon="home")
    ).add_to(m)

# ==========================================
# 4. PLOTTING THE CUSTOMER UNIVERSE
# ==========================================
print(f"📍 Mapping {len(df)} customers onto the grid...")

# Iterate through all 640 customers in the CSV
for _, row in df.iterrows():
    
    # VISUAL LOGIC: 
    # Green = Good Data (System pin is perfectly verified)
    # Red = Noisy Data (System pin is vague/unverified, driver will struggle)
    color = "green" if row['is_location_verified'] else "red"
    
    # Add a small dot for the customer
    folium.CircleMarker(
        location=[row['gps_lat'], row['gps_lng']],
        radius=3,               # Small radius so the map doesn't look cluttered
        color=color,
        fill=True,
        fill_opacity=0.7,
        # Create a popup that shows the customer's latent ML profile if you click on them
        popup=(f"ID: {row['customer_id']}<br>"
               f"Type: {row['location_type']}<br>"
               f"Verified: {row['is_location_verified']}")
    ).add_to(m)

# ==========================================
# 5. EXPORT TO HTML
# ==========================================
# Folium does not output image files; it outputs an interactive HTML webpage.
os.makedirs("maps", exist_ok=True)
map_path = "maps/customer_universe.html"
m.save(map_path)

print(f"✅ Success! Map generated at: {os.path.abspath(map_path)}")
print("👉 Open this HTML file in your browser to see your world!")