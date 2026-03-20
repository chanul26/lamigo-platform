import pandas as pd
import folium
import config
import os

# 1. Load the generated customer data
try:
    df = pd.read_csv("data/raw/customers.csv")
except FileNotFoundError:
    print("❌ Error: customers.csv not found. Run src/00_generate_seed_assets.py first!")
    exit()

# 2. Initialize a map centered on Sri Lanka
# We zoom out just enough to see both Colombo and Galle
m = folium.Map(location=[6.45, 80.05], zoom_start=9, tiles="cartodbpositron")

# 3. Add the Branch Service Polygons (The "Fences")
for b_id, b_data in config.BRANCH_CONFIGURATIONS.items():
    # Folium expects [Lat, Lng], but our config is [Lng, Lat]. We swap them here.
    coords = [[p[1], p[0]] for p in b_data["service_area_polygon"]]
    
    # Give Colombo and Galle different border colors
    poly_color = "blue" if b_id == "B_001" else "purple"
    
    folium.Polygon(
        locations=coords,
        color=poly_color,
        fill=True,
        fill_color=poly_color,
        fill_opacity=0.15,
        popup=f"Service Area: {b_data['facility_name']}"
    ).add_to(m)
    
    # Add a bold marker for the Hub building itself
    folium.Marker(
        location=[b_data["origin_coordinates"]["latitude"], b_data["origin_coordinates"]["longitude"]],
        popup=f"HUB: {b_data['facility_name']}",
        icon=folium.Icon(color="black", icon="home")
    ).add_to(m)

# 4. Plot the 640 Customers
print(f"📍 Mapping {len(df)} customers onto the grid...")

for _, row in df.iterrows():
    # Color logic: Green = Verified (Clean Data), Red = Unverified (The 30% Noise)
    color = "green" if row['is_location_verified'] else "red"
    
    folium.CircleMarker(
        location=[row['gps_lat'], row['gps_lng']],
        radius=3,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=(f"ID: {row['customer_id']}<br>"
               f"Type: {row['location_type']}<br>"
               f"Verified: {row['is_location_verified']}")
    ).add_to(m)

# 5. Save the final interactive HTML map
os.makedirs("maps", exist_ok=True)
map_path = "maps/customer_universe.html"
m.save(map_path)

print(f"✅ Success! Map generated at: {os.path.abspath(map_path)}")
print("👉 Open this HTML file in your browser to see your world!")