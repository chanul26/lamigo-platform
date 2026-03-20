import pandas as pd
import numpy as np
import random
import config  # Assumes config.py is in src/
from shapely.geometry import Point, Polygon
import os

# ==========================================
# REPRODUCIBILITY SEED
# ==========================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# --- HELPER: GEOGRAPHIC REJECTION SAMPLING ---
def get_random_point_in_polygon(poly_coords):
    poly = Polygon(poly_coords)
    min_lng, min_lat, max_lng, max_lat = poly.bounds
    while True:
        random_lng = random.uniform(min_lng, max_lng)
        random_lat = random.uniform(min_lat, max_lat)
        point = Point(random_lng, random_lat)
        if poly.contains(point):
            return random_lat, random_lng

# --- CORE GENERATOR: BRANCHES ---
def generate_branches():
    branches = []
    for b_id, data in config.BRANCH_CONFIGURATIONS.items():
        branches.append({
            "branch_id": b_id,
            "name": data["facility_name"],
            "lat": data["origin_coordinates"]["latitude"],
            "lng": data["origin_coordinates"]["longitude"],
            "fleet_size": data["allocated_fleet_size"]
        })
    return pd.DataFrame(branches)

# --- CORE GENERATOR: CUSTOMERS ---
def generate_customers():
    customers = []
    customer_counter = 1
    
    # DYNAMIC WORKLOAD CALCULATION
    total_fleet = sum(data["allocated_fleet_size"] for data in config.BRANCH_CONFIGURATIONS.values())
    branch_split = {}
    customers_allocated = 0
    
    branch_ids = list(config.BRANCH_CONFIGURATIONS.keys())
    for i, b_id in enumerate(branch_ids):
        if i == len(branch_ids) - 1:
            branch_split[b_id] = config.TOTAL_CUSTOMER_POPULATION - customers_allocated
        else:
            proportion = config.BRANCH_CONFIGURATIONS[b_id]["allocated_fleet_size"] / total_fleet
            count = int(config.TOTAL_CUSTOMER_POPULATION * proportion)
            branch_split[b_id] = count
            customers_allocated += count

    for branch_id, count in branch_split.items():
        branch_data = config.BRANCH_CONFIGURATIONS[branch_id]
        for _ in range(count):
            lat, lng = get_random_point_in_polygon(branch_data["service_area_polygon"])
            loc_type = np.random.choice(config.LOCATION_CHOICES, p=branch_data["location_type_probs"])
            
            # Correlated Verification Logic
            if loc_type == 'OTHER':
                is_verified = np.random.choice([True, False], p=[0.20, 0.80])
            else:
                is_verified = np.random.choice([True, False], p=[0.85, 0.15])
            
            floor = random.randint(1, 15) if loc_type in ['APARTMENT', 'OFFICE'] else 0
            
            customers.append({
                "customer_id": f"C_{customer_counter:03d}",
                "branch_id": branch_id,
                "gps_lat": round(lat, 6),
                "gps_lng": round(lng, 6),
                "location_type": loc_type,
                "floor_number": floor,
                "is_location_verified": is_verified,
                "sociability_index": round(random.uniform(0.0, 1.0), 2),
                "payment_readiness": round(random.uniform(0.1, 1.0), 2),
                "phone_responsiveness": random.choice(['HIGH', 'MEDIUM', 'LOW']),
                "access_difficulty_multiplier": round(random.uniform(1.0, 1.5), 2)
            })
            customer_counter += 1
    return pd.DataFrame(customers)

# --- CORE GENERATOR: DRIVERS (1 Lorry Per Branch Logic) ---
def generate_drivers():
    drivers = []
    driver_counter = 1
    
    for branch_id, branch_data in config.BRANCH_CONFIGURATIONS.items():
        fleet_size = branch_data["allocated_fleet_size"]
        branch_pool = ['LORRY'] + (['MOTORCYCLE'] * (fleet_size - 1))
        random.shuffle(branch_pool) 
        
        for vehicle in branch_pool:
            drivers.append({
                "driver_id": f"D_{driver_counter:03d}",
                "branch_id": branch_id,
                "vehicle_type": vehicle,
                "navigation_multiplier": round(np.random.normal(1.0, 0.1), 2),
                "handover_speed_rating": random.choice(['FAST', 'AVERAGE', 'SLOW']),
                "cod_handling_efficiency": round(random.uniform(0.2, 1.0), 2),
                "sociability_index": round(random.uniform(0.0, 1.0), 2)
            })
            driver_counter += 1
    return pd.DataFrame(drivers)

# --- EXECUTION ENGINE ---
if __name__ == "__main__":
    output_path = "data/raw" 
    os.makedirs(output_path, exist_ok=True)

    df_branches = generate_branches()
    df_drivers = generate_drivers()
    df_customers = generate_customers()
    
    df_branches.to_csv(f"{output_path}/branches.csv", index=False)
    df_drivers.to_csv(f"{output_path}/drivers.csv", index=False)
    df_customers.to_csv(f"{output_path}/customers.csv", index=False)

    # ==========================================
    # FORMATTED TERMINAL DASHBOARD
    # ==========================================
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
        # Clean up "Hub Hub" redundancy dynamically
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
        
        # Drivers (Condensed to one clean line)
        b_drivers = df_drivers[df_drivers['branch_id'] == b_id]
        mc_count = len(b_drivers[b_drivers['vehicle_type'] == 'MOTORCYCLE'])
        lorry_count = len(b_drivers[b_drivers['vehicle_type'] == 'LORRY'])
        print(f"   🚚 Drivers   : {len(b_drivers)} ({mc_count} Motorcycles, {lorry_count} Lorry)")
        
        # Customers (With perfectly aligned percentage columns)
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