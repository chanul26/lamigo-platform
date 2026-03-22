import pandas as pd
import numpy as np
import math
import random
import hashlib
import h3  # pip install h3

# --- CONSTANTS ---
LKR_NOTES_AND_COINS = [5000, 1000, 500, 100, 50, 20, 10, 5]

# ==========================================
# HELPER 1: SPATIAL GRID (H3)
# ==========================================
def get_h3_grid_id(lat, lng, resolution=8):
    """
    Converts raw continuous GPS coordinates into a discrete Hexagonal Grid ID.
    Resolution 8 creates hexagons of ~0.7 km^2. 
    In ML terms, this turns infinite geographic space into a Finite Categorical Feature 
    that an Embedding Layer can easily memorize.
    """
    try:
        # For newer h3-py versions (4.x+)
        return h3.latlng_to_cell(lat, lng, resolution)
    except AttributeError:
        # Fallback for older h3-py versions (3.x)
        return h3.geo_to_h3(lat, lng, resolution)

# ==========================================
# HELPER 2: CASH FRICTION COMBINATORICS
# ==========================================
def calculate_cash_friction_category(cod_amount):
    """
    Simulates physical cash handover. It calculates the minimum number of physical 
    notes/coins exchanged between the customer and driver.
    Returns a Sparse Categorical ID (0-20) representing physical friction.
    """
    if pd.isna(cod_amount) or cod_amount <= 0:
        return 0 
        
    working_amount = math.ceil(cod_amount / 5.0) * 5
    
    # Randomly simulate what the customer hands the driver
    payment_strategy = random.random()
    
    if payment_strategy < 0.20:
        tendered = working_amount # Exact change!
    elif payment_strategy < 0.50:
        if working_amount % 500 > 0 and working_amount % 500 > 400:
            tendered = math.ceil(working_amount / 500.0) * 500
        else:
            tendered = math.ceil(working_amount / 100.0) * 100
    elif payment_strategy < 0.85:
        tendered = math.ceil(working_amount / 1000.0) * 1000
    else:
        tendered = math.ceil(working_amount / 5000.0) * 5000
        if tendered == working_amount: tendered += 5000

    change = tendered - working_amount
    
    # Greedy algorithm to count the physical notes used
    def count_notes(amt):
        count, rem = 0, amt
        for note in LKR_NOTES_AND_COINS:
            if rem >= note:
                count += rem // note
                rem = rem % note
        return int(count)

    total_items = count_notes(tendered) + count_notes(change)
    # Cap the friction class at 20 notes to prevent huge categorical embedding tables
    return min(total_items, 20)

# ==========================================
# MASTER WRAPPER FUNCTION
# ==========================================
def generate_ml_features(trip_df, current_date, hub_lat, hub_lng):
    """
    Takes a primitive sequenced trip dataframe and derives all ML features 
    required by the DeepFM schema (except time labels).
    """
    # Ensure the dataframe is strictly sorted by sequence_no before shifting
    trip_df = trip_df.sort_values('sequence_no').copy()
    
    trip_id = trip_df.iloc[0]['trip_id']
    
    # ==========================================
    # REPRODUCIBILITY: TRIP-BASED SEEDING
    # ==========================================
    # Ensures the simulated payment behaviors (notes tendered) are identical 
    # every time we run this specific trip.
    trip_seed = int(hashlib.md5(trip_id.encode('utf-8')).hexdigest(), 16) % (2**32)
    random.seed(trip_seed)
    
    # Rename vehicle_type to exactly match schema requirements
    if 'vehicle_type' in trip_df.columns:
        trip_df.rename(columns={'vehicle_type': 'vehicle_type_id'}, inplace=True)
    
    # ==========================================
    # 1. TEMPORAL FEATURES
    # ==========================================
    # Derived from the master simulation date
    trip_df['month_of_year'] = current_date.month
    trip_df['day_of_week'] = current_date.weekday() # 0 = Monday, 6 = Sunday
    
    # ==========================================
    # 2. SPATIAL FEATURES (H3)
    # ==========================================
    trip_df['destination_grid_id'] = trip_df.apply(
        lambda row: get_h3_grid_id(row['gps_lat'], row['gps_lng']), axis=1
    )
    
    # Calculate the Hub's grid ID to inject into Stop 1 later
    hub_grid_id = get_h3_grid_id(hub_lat, hub_lng)
    
    # ==========================================
    # 3. PACING & FATIGUE FEATURES
    # ==========================================
    total_stops = len(trip_df)
    trip_df['total_stops'] = total_stops
    trip_df['trip_sequence_num'] = trip_df['sequence_no'].astype(float)
    trip_df['trip_sequence_id'] = trip_df['sequence_no'].astype(int)
    
    # Ratio (Dense variable for DeepFM) and Bin (Sparse Categorical 0-20 for DeepFM)
    trip_df['trip_progress_ratio'] = (trip_df['sequence_no'] / total_stops).round(2)
    trip_df['trip_progress_id'] = (trip_df['trip_progress_ratio'] * 20).astype(int).clip(upper=20)
    
    # ==========================================
    # 4. CURRENT CASH FRICTION
    # ==========================================
    # Generate the current stop's friction code (to be shifted for the next leg)
    # Ensure HUB_RETURN doesn't throw errors by filling NaNs with 0
    trip_df['cod_amount'] = trip_df['cod_amount'].fillna(0.0) 
    trip_df['cod_friction_code'] = trip_df['cod_amount'].apply(calculate_cash_friction_category)
    
    # ==========================================
    # 5. THE HANDOVER LAG SHIFTS (Critical ML Step)
    # ==========================================
    # To predict the time to arrive at Stop N, the model needs to know the context 
    # of Stop N-1 (because the driver is physically leaving Stop N-1).
    branch_id = trip_df.iloc[0]['branch_id']
    
    # Shift Identities (Stop 1's previous customer is the Hub itself)
    trip_df['prev_customer_id'] = trip_df['customer_id'].shift(1).fillna(f"HUB_{branch_id}")
    
    # Shift Locations
    trip_df['origin_grid_id'] = trip_df['destination_grid_id'].shift(1).fillna(hub_grid_id)
    
    # Shift Context (If 'true_location_type' exists, use it. Otherwise fallback to 'location_type')
    loc_col = 'true_location_type' if 'true_location_type' in trip_df.columns else 'location_type'
    trip_df['prev_location_type'] = trip_df[loc_col].shift(1).fillna('HUB') # Hubs act like a HUB
    
    # Shift Financials (The driver collected zero cash at the hub prior to Stop 1)
    trip_df['prev_cod_amount'] = trip_df['cod_amount'].shift(1).fillna(0.0)
    trip_df['prev_cod_friction_code'] = trip_df['cod_friction_code'].shift(1).fillna(0)
    
    return trip_df