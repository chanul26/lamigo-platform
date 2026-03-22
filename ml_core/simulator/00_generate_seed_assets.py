import pandas as pd
import numpy as np
import random
from shapely.geometry import Point, Polygon
import sys
import os

# ==========================================
# PATH FIX: Point to root
# ==========================================
# This ensures that no matter where you run the script from in your terminal,
# Python knows to look in the parent directory to find the 'simulator' package.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config  # Imports the static rules from simulator/config.py

# ==========================================
# REPRODUCIBILITY SEED
# ==========================================
# In Machine Learning, randomness must be controllable. By setting a seed, 
# we guarantee that if someone else runs this code 5 years from now, 
# they will get the exact same 640 customers and 20 drivers.
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# --- HELPER: GEOGRAPHIC REJECTION SAMPLING ---

def get_random_point_in_polygon(poly_coords):
    """
    Generates a random GPS coordinate that is strictly INSIDE a given polygon.
    
    How it works (Rejection Sampling):
    1. It draws a square "bounding box" around the weirdly shaped polygon.
    2. It throws a dart randomly inside the square box.
    3. If the dart lands outside the polygon (but inside the box), it throws again.
    4. It repeats until the dart lands inside the polygon.
    """
    poly = Polygon(poly_coords)
    # Get the bounding box of the polygon (min/max latitudes and longitudes)
    min_lng, min_lat, max_lng, max_lat = poly.bounds
    
    while True:
        # Generate a random point within the square bounding box
        random_lng = random.uniform(min_lng, max_lng)
        random_lat = random.uniform(min_lat, max_lat)
        point = Point(random_lng, random_lat)
        
        # Check if the random point is actually inside the complex polygon shape
        if poly.contains(point):
            return random_lat, random_lng

# --- CORE GENERATOR: BRANCHES ---
def generate_branches():
    """
    Reads the configuration file and creates the physical branch/hub locations.
    """
    branches = []
    # Loop through B_001 (Colombo) and B_002 (Galle) defined in config.py
    for b_id, data in config.BRANCH_CONFIGURATIONS.items():
        branches.append({
            "branch_id": b_id,
            "name": data["facility_name"],
            # Extract the exact door/gate GPS coordinates of the warehouse
            "lat": data["origin_coordinates"]["latitude"],
            "lng": data["origin_coordinates"]["longitude"],
            "fleet_size": data["allocated_fleet_size"]
        })
    return pd.DataFrame(branches)

# --- CORE GENERATOR: CUSTOMERS ---
def generate_customers():
    """
    Generates the 640 unique customers. It distributes them geographically 
    and assigns them "Hidden DNA" traits that will simulate physical delays later.
    """
    customers = []
    customer_counter = 1
    
    # --- DYNAMIC WORKLOAD CALCULATION ---
    # We want to distribute the 640 customers fairly based on how many drivers a branch has.
    # E.g., If Colombo has 12 drivers and Galle has 8, Colombo gets 60% of the customers.
    total_fleet = sum(data["allocated_fleet_size"] for data in config.BRANCH_CONFIGURATIONS.values())
    branch_split = {}
    customers_allocated = 0
    
    branch_ids = list(config.BRANCH_CONFIGURATIONS.keys())
    for i, b_id in enumerate(branch_ids):
        # If it's the last branch, give it whatever customers are left to avoid rounding errors
        if i == len(branch_ids) - 1:
            branch_split[b_id] = config.TOTAL_CUSTOMER_POPULATION - customers_allocated
        else:
            # Calculate proportion (e.g., 12 / 20 = 0.6)
            proportion = config.BRANCH_CONFIGURATIONS[b_id]["allocated_fleet_size"] / total_fleet
            count = int(config.TOTAL_CUSTOMER_POPULATION * proportion)
            branch_split[b_id] = count
            customers_allocated += count

    # --- CUSTOMER SPAWNING ---
    for branch_id, count in branch_split.items():
        branch_data = config.BRANCH_CONFIGURATIONS[branch_id]
        
        # Create 'count' number of customers for this branch
        for _ in range(count):
            # 1. Spawn them geographically inside the branch's service area
            lat, lng = get_random_point_in_polygon(branch_data["service_area_polygon"])
            
            # 2. Assign their building type (based on branch demographics in config)
            loc_type = np.random.choice(config.LOCATION_CHOICES, p=branch_data["location_type_probs"])
            
            # 3. Correlated Verification Logic
            # If the system says 'OTHER', it means the user didn't fill out their profile well.
            # Therefore, they have an 80% chance of having a bad/unverified GPS pin.
            if loc_type == 'OTHER':
                is_verified = np.random.choice([True, False], p=[0.20, 0.80])
            else:
                is_verified = np.random.choice([True, False], p=[0.85, 0.15])
            
            # 4. Floor logic (Only apartments and offices have high floors, which cause elevator delays)
            floor = random.randint(1, 15) if loc_type in ['APARTMENT', 'OFFICE'] else 0
            
            # 5. Append all data (including the hidden traits used by the physics engine)
            customers.append({
                "customer_id": f"C_{customer_counter:03d}",
                "branch_id": branch_id,
                "gps_lat": round(lat, 6),
                "gps_lng": round(lng, 6),
                "location_type": loc_type,
                "floor_number": floor,
                "is_location_verified": is_verified,
                "sociability_index": round(random.uniform(0.0, 1.0), 2),     # Determines if they chat with the driver
                "payment_readiness": round(random.uniform(0.1, 1.0), 2),     # Determines how fast they find COD cash
                "phone_responsiveness": random.choice(['HIGH', 'MEDIUM', 'LOW']), # Determines search delay if pin is bad
                "access_difficulty_multiplier": round(random.uniform(1.0, 1.5), 2) # e.g., security gates
            })
            customer_counter += 1
            
    return pd.DataFrame(customers)

# --- CORE GENERATOR: DRIVERS ---
def generate_drivers():
    """
    Creates the workforce. Assigns exactly 1 Lorry per branch, 
    and fills the rest of the fleet capacity with Motorcycles.
    """
    drivers = []
    driver_counter = 1
    
    for branch_id, branch_data in config.BRANCH_CONFIGURATIONS.items():
        fleet_size = branch_data["allocated_fleet_size"]
        
        # Create a list with exactly 1 'LORRY', and the rest 'MOTORCYCLE'
        branch_pool = ['LORRY'] + (['MOTORCYCLE'] * (fleet_size - 1))
        random.shuffle(branch_pool) # Shuffle so driver D_001 isn't always the lorry
        
        for vehicle in branch_pool:
            drivers.append({
                "driver_id": f"D_{driver_counter:03d}",
                "branch_id": branch_id,
                "vehicle_type": vehicle,
                # --- LATENT BEHAVIORAL TRAITS ---
                # navigation_multiplier: <1.0 means they drive faster than Google Maps predicts
                "navigation_multiplier": round(np.random.normal(1.0, 0.1), 2),
                # handover_speed: Affects time spent walking out of buildings
                "handover_speed_rating": random.choice(['FAST', 'AVERAGE', 'SLOW']),
                # cod_handling: How fast they count cash
                "cod_handling_efficiency": round(random.uniform(0.2, 1.0), 2),
                # sociability: If high, and customer is high, they get stuck talking
                "sociability_index": round(random.uniform(0.0, 1.0), 2)
            })
            driver_counter += 1
            
    return pd.DataFrame(drivers)

# --- EXECUTION ENGINE ---
if __name__ == "__main__":
    # Ensure the 'data/raw' directory exists so we can save the files
    output_path = "data/raw" 
    os.makedirs(output_path, exist_ok=True)

    # Generate the assets
    df_branches = generate_branches()
    df_drivers = generate_drivers()
    df_customers = generate_customers()
    
    # Save the assets to the read-only 'raw' directory
    df_branches.to_csv(f"{output_path}/branches.csv", index=False)
    df_drivers.to_csv(f"{output_path}/drivers.csv", index=False)
    df_customers.to_csv(f"{output_path}/customers.csv", index=False)

    # ==========================================
    # FORMATTED TERMINAL DASHBOARD
    # ==========================================
    # This prints a nice summary to the terminal so you can verify the logic worked.
    print("\n" + "="*50)
    print(f" 🚀 LamiGo ASSET GENERATION SUMMARY (Seed: {SEED})")
    print("="*50)
    
    v_counts = df_drivers['vehicle_type'].value_counts()
    print(f"\n✅ TOTAL DRIVERS:   {len(df_drivers)}")
    print(f"   - Motorcycles:   {v_counts.get('MOTORCYCLE', 0)}")
    print(f"   - Three-Wheels:  0") 
    print(f"   - Lorries:       {v_counts.get('LORRY', 0)}")
    
    print(f"\n✅ TOTAL CUSTOMERS: {len(df_customers)}")
    c_counts = df_customers['branch_id'].value_counts()
    for b_id, b_data in config.BRANCH_CONFIGURATIONS.items():
        # Clean up "Hub Hub" redundancy dynamically for printing
        clean_name = b_data['facility_name'].replace(" Hub", "")
        print(f"   - {clean_name:<14} Hub: {c_counts.get(b_id, 0)}")
    
    unverified = len(df_customers[df_customers['is_location_verified'] == False])
    print(f"\n⚠️  UNVERIFIED PINS: {unverified} ({unverified/len(df_customers):.1%})")
    
    print("\n" + "-"*50)
    print(" 🏙️  BRANCH-SPECIFIC OVERVIEW")
    print("-"*50)

    for b_id in config.BRANCH_CONFIGURATIONS.keys():
        b_name = config.BRANCH_CONFIGURATIONS[b_id]['facility_name']
        print(f"\n📍 {b_name} ({b_id})")
        
        # Print Driver stats for the branch
        b_drivers = df_drivers[df_drivers['branch_id'] == b_id]
        mc_count = len(b_drivers[b_drivers['vehicle_type'] == 'MOTORCYCLE'])
        lorry_count = len(b_drivers[b_drivers['vehicle_type'] == 'LORRY'])
        print(f"   🚚 Drivers   : {len(b_drivers)} ({mc_count} Motorcycles, {lorry_count} Lorry)")
        
        # Print Customer Demographics for the branch
        b_customers = df_customers[df_customers['branch_id'] == b_id]
        print(f"   👥 Customers : {len(b_customers)}")
        
        loc_dist = b_customers['location_type'].value_counts()
        for loc in config.LOCATION_CHOICES:
            count = loc_dist.get(loc, 0)
            print(f"      - {loc:<12}: {count:<3} ({count/len(b_customers):>5.1%})")
            
        b_unverified = len(b_customers[b_customers['is_location_verified'] == False])
        print(f"      [!] Unverified: {b_unverified:<3} ({b_unverified/len(b_customers):>5.1%})")

    print("\n" + "="*50)
    print(f"📂 Assets saved to: {os.path.abspath(output_path)}")
    print("="*50 + "\n")