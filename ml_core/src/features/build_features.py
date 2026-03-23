import pandas as pd
import numpy as np
import h3
import math
import random
import os

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
# The physical currency notes/coins available in Sri Lanka
LKR_NOTES_AND_COINS = [5000, 1000, 500, 100, 50, 20, 10, 5]

# H3 Resolution: 8 yields hex bins of ~0.7 square kilometers (ideal for neighborhood-level traffic/friction)
H3_RESOLUTION = 8

def calculate_cash_friction_category(cod_amount):
    """
    Simulates physical cash handover friction (Feature 14).
    Calculates the minimum number of physical notes/coins exchanged between 
    the customer and driver. Returns a Sparse Categorical ID (0-20).
    """
    if pd.isna(cod_amount) or cod_amount <= 0:
        return 0 
        
    # Round to nearest 5 Rupee coin for realism
    working_amount = math.ceil(cod_amount / 5.0) * 5
    
    # Randomly simulate what the customer hands the driver
    payment_strategy = random.random()
    
    if payment_strategy < 0.20:
        tendered = working_amount  # Exact change
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
    
    # Cap the friction class at 20 notes to prevent memory explosion in the embedding layer
    return min(total_items, 20)

def derive_features(df):
    """
    Core transformation logic mapping raw Bronze data to Silver ML features.
    Aligns strictly with Thesis Tables 3.2.1, 3.2.2, and 3.2.3.
    """
    print("⏳ Parsing datetime columns...")
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['arrival_time'] = pd.to_datetime(df['arrival_time'])

    # -------------------------------------------------------------------
    # TARGET VARIABLE (Table 3.2.1)
    # -------------------------------------------------------------------
    print("🎯 Calculating Regression Target (actual_time_diff_seconds)...")
    # Step 1: Real travel time
    df['actual_travel_seconds'] = (df['arrival_time'] - df['start_time']).dt.total_seconds()
    # Step 2: Target = Real - Predicted
    df['actual_time_diff_seconds'] = df['actual_travel_seconds'] - df['google_eta_seconds']

    # -------------------------------------------------------------------
    # TEMPORAL FEATURES (Table 3.2.2 - Items 11, 12, 13)
    # -------------------------------------------------------------------
    print("⏰ Extracting temporal features...")
    df['hour_of_day'] = df['start_time'].dt.hour
    df['day_of_week'] = df['start_time'].dt.dayofweek
    df['month_of_year'] = df['start_time'].dt.month

    # -------------------------------------------------------------------
    # SPATIAL FEATURES (Table 3.2.2 - Item 4)
    # -------------------------------------------------------------------
    print(f"🗺️ Embedding GPS into H3 Spatial Grids (Resolution {H3_RESOLUTION})...")
    # UPDATED: Changed from geo_to_h3 to latlng_to_cell for h3 v4 compatibility
    df['destination_grid_id'] = df.apply(
        lambda row: h3.latlng_to_cell(row['latitude'], row['longitude'], H3_RESOLUTION), axis=1
    )

    # -------------------------------------------------------------------
    # LAG FEATURES & EDGE CASE HANDLING (Table 3.2.2 & 3.2.3)
    # -------------------------------------------------------------------
    print("🔄 Shifting rows to create 'Previous Stop' (Lag) features...")
    # CRITICAL: We must sort by trip and sequence_no before shifting, 
    # otherwise we will steal data from another driver's trip!
    df = df.sort_values(by=['trip_id', 'sequence_no']).reset_index(drop=True)

    # Shift columns down by 1 within each trip
    df['prev_customer_id'] = df.groupby('trip_id')['customer_id'].shift(1)
    df['prev_location_type'] = df.groupby('trip_id')['location_type'].shift(1)
    df['prev_cod_amount'] = df.groupby('trip_id')['cod_amount'].shift(1)
    df['origin_grid_id'] = df.groupby('trip_id')['destination_grid_id'].shift(1)

    # EDGE CASE: Sequence 1 has no "previous" customer because they just left the Hub.
    # We dynamically use the 'branch_id' to label the origin properly.
    is_first_stop = df['sequence_no'] == 1
    
    df.loc[is_first_stop, 'prev_customer_id'] = 'HUB_' + df.loc[is_first_stop, 'branch_id']
    df.loc[is_first_stop, 'prev_location_type'] = 'HUB'
    df.loc[is_first_stop, 'prev_cod_amount'] = 0.0
    # The origin grid of Stop 1 is simply the Hub's identifier
    df.loc[is_first_stop, 'origin_grid_id'] = 'HUB_' + df.loc[is_first_stop, 'branch_id']

    # -------------------------------------------------------------------
    # CASH FRICTION CALCULATION (Table 3.2.2 - Item 14)
    # -------------------------------------------------------------------
    print("💵 Processing COD friction classes...")
    df['prev_cod_friction_code'] = df['prev_cod_amount'].apply(calculate_cash_friction_category)

    # -------------------------------------------------------------------
    # FATIGUE & PACING FEATURES (Table 3.2.2 & 3.2.3)
    # -------------------------------------------------------------------
    print("🔋 Calculating workload and pacing metrics...")
    # Rename for exact matching with Table 3.2.3
    df.rename(columns={'google_dist_meters': 'google_distance_meters'}, inplace=True)
    
    # Dense fatigue features
    df['trip_sequence_num'] = df['sequence_no']
    df['trip_progress_ratio'] = (df['sequence_no'] / df['total_stops']).round(2)
    
    # Sparse fatigue features (Categorical mappings)
    df['trip_sequence_id'] = df['sequence_no'].astype(str)
    df['trip_progress_id'] = (df['trip_progress_ratio'] * 20).astype(int).astype(str)

    return df

def main(input_file, output_file):
    print("="*50)
    print("🚀 INITIALIZING LAMIGO FEATURE ENGINEERING PIPELINE")
    print("="*50)

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"❌ Input file not found: {input_file}")

    # 1. Load the dataset
    print(f"📥 Loading Bronze Dataset: {input_file}")
    df_raw = pd.read_csv(input_file)
    print(f"📊 Rows loaded: {len(df_raw):,}")

    # 2. Derive all features
    df_silver = derive_features(df_raw)

    # 3. Define the final output schema explicitly to match thesis tables
    final_columns = [
        # Target
        'actual_time_diff_seconds',
        
        # Table 3.2.2: Sparse Categorical Features
        'driver_id', 'prev_customer_id', 'customer_id', 'destination_grid_id', 
        'origin_grid_id', 'vehicle_type_id', 'location_type', 'prev_location_type', 
        'is_pin_verified', 'weather_code', 'month_of_year', 'day_of_week', 
        'hour_of_day', 'prev_cod_friction_code', 'trip_sequence_id', 'trip_progress_id',
        
        # Table 3.2.3: Dense Numerical Features
        'google_eta_seconds', 'google_distance_meters', 'prev_cod_amount', 
        'rain_volume_1h', 'trip_sequence_num', 'trip_progress_ratio',
        
        # Contextual columns kept for debugging or joining (optional but helpful for EDA)
        'trip_id', 'branch_id', 'date'
    ]

    # Filter to only the columns we strictly need
    df_silver = df_silver[final_columns]

    # 4. Save to disk
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(f"💾 Saving Silver Dataset to: {output_file}")
    df_silver.to_csv(output_file, index=False)
    
    print("="*50)
    print("✅ FEATURE PIPELINE COMPLETE!")
    print("="*50)

if __name__ == "__main__":
    # Ensure this script works regardless of where it's executed from (root or inside src/)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    INPUT_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'raw_historical_deliveries.csv')
    OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'silver_historical_deliveries.csv')
    
    main(INPUT_PATH, OUTPUT_PATH)