import pandas as pd
import numpy as np
import math
import hashlib

# ==========================================
# CONSTANTS: THE "PHYSICS" OF SRI LANKAN ROADS
# ==========================================

# 1. Detour Factor: How much longer is the road compared to a flying bird?
# A straight line (Haversine) is never the actual driving distance. 
# Cities with grids (Colombo) require more turning and zig-zagging than coastal highways (Galle).
DETOUR_FACTORS = {
    "B_001": 1.45,  # Colombo: Road distance is ~45% longer than a straight line
    "B_002": 1.25   # Galle: Road distance is ~25% longer than a straight line
}

# 2. Average Speeds in km/h 
# These are carefully dialed to balance pure driving times.
SPEEDS_KMH = {
    "B_001": { # Colombo (Heavy Traffic, traffic lights, one-ways)
        "MOTORCYCLE": 20.0, 
        "LORRY": 10.0       
    },
    "B_002": { # Galle (Moderate Traffic, open coastal roads)
        "MOTORCYCLE": 28.0, 
        "LORRY": 18.0       
    }
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the straight-line (Euclidean) distance in meters between two GPS coordinates 
    accounting for the curvature of the Earth.
    """
    R = 6371000  # Radius of the Earth in meters
    phi_1, phi_2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ==========================================
# MAIN SIMULATION ENGINE
# ==========================================
def calculate_google_metrics(trip_df, hub_lat, hub_lng):
    """
    Takes a sequenced trip and simulates what Google Maps would predict 
    for the distance and ETA between each stop at the exact moment of dispatch.
    """
    google_distances = []
    google_etas = []
    
    # Extract trip context
    branch_id = trip_df.iloc[0]['branch_id']
    trip_id = trip_df.iloc[0]['trip_id']
    
    # ==========================================
    # REPRODUCIBILITY: TRIP-BASED SEEDING
    # ==========================================
    # We hash the unique 'trip_id' (e.g., TRIP_20200515_B_001_D_002) into an integer.
    # This guarantees that the "Traffic Noise" for this exact trip is identical 
    # every time the simulation is run.
    trip_seed = int(hashlib.md5(trip_id.encode('utf-8')).hexdigest(), 16) % (2**32)
    np.random.seed(trip_seed)
    
    # ==========================================
    # SAFE COLUMN CHECK
    # ==========================================
    # Feature Engineering renames 'vehicle_type' to 'vehicle_type_id'.
    # This safe check ensures the engine doesn't crash regardless of when it runs.
    veh_col = 'vehicle_type_id' if 'vehicle_type_id' in trip_df.columns else 'vehicle_type'
    vehicle_type = trip_df.iloc[0][veh_col]
    
    # Safely convert integer IDs back to string keys if needed (1=Motorcycle, 2=Lorry)
    if str(vehicle_type) == '1' or vehicle_type == 'MOTORCYCLE':
        veh_key = 'MOTORCYCLE'
    else:
        veh_key = 'LORRY'
        
    # Get the Physics constraints for this specific city and vehicle
    detour_multiplier = DETOUR_FACTORS.get(branch_id, 1.3)
    speed_kmh = SPEEDS_KMH.get(branch_id, {}).get(veh_key, 15.0)
    
    # Convert speed from km/h to meters per second (m/s = km/h / 3.6)
    speed_mps = speed_kmh / 3.6 
    
    # Initialize the starting location as the Hub
    prev_lat = hub_lat
    prev_lng = hub_lng
    
    # Iterate through every delivery stop chronologically
    for _, row in trip_df.iterrows():
        # 1. Calculate pure straight-line distance
        straight_dist = haversine_distance(prev_lat, prev_lng, row['gps_lat'], row['gps_lng'])
        
        # 2. Apply Detour Factor to simulate actual turning road distance
        road_dist_meters = int(straight_dist * detour_multiplier)
        
        # 3. Calculate Base ETA (Time = Distance / Speed)
        base_eta_seconds = road_dist_meters / speed_mps
        
        # 4. Add "Google Traffic Noise" 
        # Google Maps ETAs are rarely mathematically perfect. We add a +/- 10% 
        # Gaussian variance to simulate the API predicting mild traffic at dispatch.
        traffic_noise = np.random.normal(loc=1.0, scale=0.10)
        final_eta_seconds = int(base_eta_seconds * traffic_noise)
        
        # Store results
        google_distances.append(road_dist_meters)
        google_etas.append(final_eta_seconds)
        
        # Update previous location so the next calculation starts from this current door
        prev_lat = row['gps_lat']
        prev_lng = row['gps_lng']
        
    # Append the simulated metrics back to the dataframe
    trip_df['google_distance_meters'] = google_distances
    trip_df['google_eta_seconds'] = google_etas
    
    return trip_df