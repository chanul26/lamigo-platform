import pandas as pd
import numpy as np
import hashlib
import random
from datetime import datetime, timedelta

# ==========================================
# PATH FIX: Point to the new graveyard folder
# ==========================================
from simulator import config

# ==========================================
# PHYSICS CONSTANTS
# ==========================================
# Base walking/access times in seconds (Without penalties)
# Walking from the parked bike to the customer's actual door
LOCATION_BASE_DELAY = {
    'HOME': 30,          # Pull up, kickstand down, walk to front gate
    'APARTMENT': 150,    # Park, enter lobby, talk to security, wait for elevator
    'OFFICE': 120,       # Park, sign in at reception
    'RETAIL_STORE': 45,  # Walk in, navigate aisles to find the manager/cashier
    'WAREHOUSE': 90,     # Find the loading bay or logistics manager
    'HUB': 0             # Instant (Handled separately as dispatch time)
}

# How long does it take to find the customer if their GPS pin is wrong?
PHONE_MULTIPLIERS = {
    'HIGH': 0.5,    # Answers immediately, gives clear landmark directions
    'MEDIUM': 1.0,  # Takes a few rings to answer
    'LOW': 2.5      # Doesn't answer, driver has to ask neighbors or wait
}

# The physical walking speed multiplier of the driver
HANDOVER_SPEEDS = {
    'FAST': 0.7,    # Driver jogs/walks very fast
    'AVERAGE': 1.0, # Normal walking speed
    'SLOW': 1.4     # Driver walks slowly
}

# ==========================================
# HELPER: DETERMINISTIC HASHING
# ==========================================
def hash_to_float(string_val):
    """
    Converts any string (like a Grid ID or Driver+Grid combo) into a permanent, 
    repeatable float between 0.0 and 1.0. 
    This ensures that Driver_04 is *always* an expert in Hex_88, across all 1500 days,
    without needing to store a massive lookup table in memory.
    """
    hash_hex = hashlib.md5(str(string_val).encode('utf-8')).hexdigest()
    # Convert first 8 characters of hex to an integer, then divide by max possible hex value
    return int(hash_hex[:8], 16) / 0xffffffff

# ==========================================
# MAIN PHYSICS ENGINE
# ==========================================
def simulate_times(trip_df, df_drivers, df_customers, current_date, shift_start_str):
    """
    Calculates the sub-additive, complex realities of physical delivery time.
    Calculates row-by-row chronologically to accurately propagate the clock.
    """
    # ==========================================
    # REPRODUCIBILITY: TRIP-BASED SEEDING
    # ==========================================
    # Lock the random number generators for the 3% Gaussian noise and the Hub dispatch delay
    trip_id = trip_df.iloc[0]['trip_id']
    trip_seed = int(hashlib.md5(trip_id.encode('utf-8')).hexdigest(), 16) % (2**32)
    random.seed(trip_seed)
    np.random.seed(trip_seed)

    # 1. Merge the missing DNA from the static tables
    # We need the hidden traits (phone responsiveness, driver speeds, etc.) that 
    # the feature engine didn't keep.
    trip_df = trip_df.merge(df_drivers[['driver_id', 'navigation_multiplier', 'handover_speed_rating', 'cod_handling_efficiency']], 
                            on='driver_id', how='left')
    
    trip_df = trip_df.merge(df_customers[['customer_id', 'phone_responsiveness', 'access_difficulty_multiplier']], 
                            on='customer_id', how='left')
    
    # Fill NaNs for the HUB_RETURN row (The Hub answers its phone immediately)
    trip_df['phone_responsiveness'] = trip_df['phone_responsiveness'].fillna('HIGH')
    trip_df['access_difficulty_multiplier'] = trip_df['access_difficulty_multiplier'].fillna(1.0)
    
    # Initialize the shift clock
    shift_start_time = datetime.strptime(shift_start_str, "%H:%M:%S").time()
    current_clock = datetime.combine(current_date, shift_start_time)
    
    # State tracking for the "Previous" customer (For the Handover calculations)
    prev_cust_sociability = 0.5
    prev_pay_readiness = 1.0
    
    start_times = []
    arrival_times = []
    actual_time_diffs = []
    hours_of_day = []
    
    branch_id = trip_df.iloc[0]['branch_id']
    mean_dispatch = config.BRANCH_CONFIGURATIONS[branch_id]['mean_dispatch_friction_sec']
    std_dispatch = config.BRANCH_CONFIGURATIONS[branch_id]['dispatch_friction_std_dev']

    # Process row by row chronologically
    for index, row in trip_df.iterrows():
        
        # ==========================================
        # 1. TIME INITIALIZATION & HUB DELAY
        # ==========================================
        if row['sequence_no'] == 1:
            # Hub loading time (Sorting packages onto the bike)
            hub_delay = np.random.normal(mean_dispatch, std_dispatch)
            # Weather penalty at Hub: Heavy rain slows down loading by 20%
            if row['rain_volume_1h'] > 5.0: hub_delay *= 1.20 
            
            start_times.append(current_clock)
            current_clock += timedelta(seconds=int(hub_delay))
            
            # The "Handover" for Stop 1 is zero (it's covered by the hub delay)
            T_handover = 0
        else:
            # For all other stops, the start time is the moment they finished the last stop
            start_times.append(current_clock)
            
            # ==========================================
            # 2. HANDOVER DELAY (Leaving the PREVIOUS stop)
            # ==========================================
            # A. Base walk out time (walking back to the bike)
            walk_out = LOCATION_BASE_DELAY.get(row['prev_location_type'], 30)
            
            # B. COD Friction (Complex Interaction)
            # Driver efficiency * Previous Customer Readiness * Number of Notes (Friction Code)
            cod_delay = 0
            if row['prev_cod_friction_code'] > 0:
                base_cod_sec = row['prev_cod_friction_code'] * 8 # 8 seconds per physical note/coin
                cod_delay = base_cod_sec * (2.0 - row['cod_handling_efficiency']) * (2.0 - prev_pay_readiness)
                
            # C. The "Chatty Customer" Penalty
            # Only triggers if BOTH driver and previous customer are highly sociable
            chat_delay = 0
            driver_soc = df_drivers[df_drivers['driver_id'] == row['driver_id']].iloc[0]['sociability_index']
            if driver_soc > 0.7 and prev_cust_sociability > 0.7:
                chat_delay = (driver_soc * prev_cust_sociability) * 180 # Up to 3 minutes talking
                
            # SUB-ADDITIVITY MATH: Drivers parallel-process tasks.
            # They count money WHILE walking out, or chat WHILE putting on their helmet.
            # Formula: Max(A, B, C) + 0.3 * Mid(A,B,C) + 0.1 * Min(A,B,C)
            delays = sorted([walk_out, cod_delay, chat_delay], reverse=True)
            T_handover = delays[0] + (0.3 * delays[1]) + (0.1 * delays[2])
            
            # Apply Driver Handover Speed Modifier
            T_handover *= HANDOVER_SPEEDS[row['handover_speed_rating']]

        # ==========================================
        # 3. DRIVE DELAY (Traffic, Weather, Grid Affinity)
        # ==========================================
        hour = current_clock.hour
        hours_of_day.append(hour)
        
        # A. Grid Density Hash (Is this Hexagon naturally crowded with traffic lights?)
        grid_density = 0.8 + (hash_to_float(row['destination_grid_id']) * 0.7) # Scales 0.8 to 1.5
        
        # B. Rush Hour Multiplier
        rush_mod = 1.0
        if hour in [8, 9, 13, 17, 18]: rush_mod = 1.4
        
        # C. Driver "Local Expert" Affinity
        # 20% chance this driver knows the shortcuts in this exact neighborhood grid
        affinity = hash_to_float(f"{row['driver_id']}_{row['destination_grid_id']}")
        expert_mod = 0.75 if affinity < 0.20 else 1.0
        
        # D. Weather Modifiers
        weather_mod = 1.0
        if row['rain_volume_1h'] > 0:
            if str(row['vehicle_type_id']) in ['MOTORCYCLE', '1']: 
                weather_mod = 1.15 + (row['rain_volume_1h'] * 0.02) # Bikes drive slow on slippery roads
            else:
                weather_mod = 1.30 + (row['rain_volume_1h'] * 0.03) # Lorries get stuck in rain traffic
                
        # Total Drive Physics
        traffic_multiplier = grid_density * rush_mod * expert_mod * weather_mod * row['navigation_multiplier']
        actual_drive_time = row['google_eta_seconds'] * traffic_multiplier
        
        # Calculate the delay *on top* of the Google ETA
        T_drive_delay = actual_drive_time - row['google_eta_seconds']

        # ==========================================
        # 4. APPROACH DELAY (Finding the current door)
        # ==========================================
        if str(row['customer_id']).startswith('HUB_'):
            T_approach = 0 # Returning to hub is instant
        else:
            # A. Base walk in (Getting past security, waiting for elevators)
            walk_in = LOCATION_BASE_DELAY.get(row['true_location_type'], 30) * row['access_difficulty_multiplier']
            
            # B. Unverified Pin / Phone Delay
            search_delay = 0
            if not row['is_pin_verified']:
                base_search = 300 # Base 5 minutes lost searching
                phone_mod = PHONE_MULTIPLIERS[row['phone_responsiveness']]
                search_delay = base_search * phone_mod
                
            # C. Rain Approach Penalty (Motorcycle drivers putting on raincoats, walking slowly)
            rain_walk_penalty = 1.0
            if row['rain_volume_1h'] > 0 and str(row['vehicle_type_id']) in ['MOTORCYCLE', '1']:
                rain_walk_penalty = 1.3
                
            # SUB-ADDITIVITY MATH: Driver calls customer WHILE dealing with the security gate
            T_approach = (max(walk_in, search_delay) + 0.3 * min(walk_in, search_delay)) * rain_walk_penalty

        # ==========================================
        # 5. FATIGUE & BREAKS (The Human Element)
        # ==========================================
        # Drivers slow down slightly with every package they deliver
        T_fatigue = row['trip_sequence_num'] * 0.5 
        
        # Lunch Break Logic (Happens between 1 PM and 3 PM, mid-route)
        if hour in [13, 14] and 0.4 <= row['trip_progress_ratio'] <= 0.6:
            # Hash the trip_id + sequence_no to deterministically trigger ONE lunch break
            lunch_hash = hash_to_float(f"{row['trip_id']}_{row['sequence_no']}")
            if lunch_hash < 0.15: # 15% chance they take lunch exactly on this stop
                T_fatigue += random.uniform(1200, 2400) # 20 to 40 minutes

        # ==========================================
        # 6. FINAL CALCULATIONS & CLOCK UPDATE
        # ==========================================
        # Total Real Duration of this leg
        leg_duration = row['google_eta_seconds'] + T_handover + T_drive_delay + T_approach + T_fatigue
        
        # Add 3% Gaussian noise so the ML model can never reach 100% perfect R-Squared.
        # (This uses the np.random.seed we locked at the top of the function!)
        leg_duration *= np.random.normal(1.0, 0.03)
        
        # Update Clock
        current_clock += timedelta(seconds=int(leg_duration))
        arrival_times.append(current_clock)
        
        # The Target Label
        actual_time_diffs.append(int(leg_duration - row['google_eta_seconds']))
        
        # Save customer traits for the NEXT row's handover math
        if not str(row['customer_id']).startswith('HUB_'):
            prev_cust_sociability = row['sociability_index']
            prev_pay_readiness = row['payment_readiness']
            
    # ==========================================
    # 7. ATTACH TO DATAFRAME & CLEANUP
    # ==========================================
    trip_df['start_time'] = start_times
    trip_df['arrival_time'] = arrival_times
    trip_df['hour_of_day'] = hours_of_day
    trip_df['actual_time_diff_seconds'] = actual_time_diffs
    
    # Drop the temporary traits we merged in just for the physics math
    # We drop them because we don't want the ML model to cheat and see the "Hidden DNA"
    cols_to_drop = ['navigation_multiplier', 'handover_speed_rating', 'cod_handling_efficiency', 
                    'phone_responsiveness', 'access_difficulty_multiplier']
    trip_df = trip_df.drop(columns=[c for c in cols_to_drop if c in trip_df.columns])
    
    return trip_df