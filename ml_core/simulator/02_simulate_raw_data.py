import pandas as pd
import datetime
import os
import sys
import time

# ==========================================
# PATH FIX: Ensure Python can find the 'simulator' package from root
# ==========================================
# Because we moved this from 'src' to 'simulator', we need to tell Python
# to look at the parent folder (ml_core) to find the local modules.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Local import (They are in the exact same folder)
import config

# 2. Absolute imports for the sub-folder engines
from simulator.engines import demand_engine, dispatch_engine, routing_engine 
from simulator.engines import distance_eta_engine, weather_engine, finance_engine, feature_engine, physics_engine
from simulator.engines.customer_state_engine import CustomerStateManager

def run_simulation():
    print("="*50)
    print("🚀 INITIALIZING LAMI-GO MASTER SIMULATION (1,500 DAYS)")
    print("="*50)

    # 1. Load the pristine Phase 1 static data
    df_customers = pd.read_csv('data/raw/customers.csv')
    df_drivers = pd.read_csv('data/raw/drivers.csv')
    df_branches = pd.read_csv('data/raw/branches.csv')

    # 2. Initialize the State Manager 
    # (This persists across all 1500 days so customers can "learn" over time)
    state_manager = CustomerStateManager(df_customers)
    
    # 3. Simulation Parameters
    start_date = datetime.date(2020, 1, 1)
    total_days = 1500
    output_file = 'data/raw/raw_historical_deliveries.csv'
    
    # Ensure directory exists before saving
    os.makedirs('data/raw', exist_ok=True)
    
    # Define the exact columns to keep for the Bronze Layer (Primitive Data)
    # Notice we drop ALL hidden DNA (like sociability) and ML Lag features.
    final_columns = [
        'trip_id', 'driver_id', 'branch_id', 'date', 'total_stops', 'vehicle_type_id',
        'customer_id', 'sequence_no', 'start_time', 'arrival_time', 
        'latitude', 'longitude', 'location_type', 'floor_number', 
        'is_pin_verified', 'cod_amount', 'google_eta_seconds', 
        'google_dist_meters', 'rain_volume_1h', 'weather_code'
    ]

    # Create an empty CSV with just the headers to initialize the file
    pd.DataFrame(columns=final_columns).to_csv(output_file, index=False)

    start_timer = time.time()

    # ==========================================
    # THE MASTER TIME LOOP
    # ==========================================
    for day_offset in range(total_days):
        current_date = start_date + datetime.timedelta(days=day_offset)
        
        # Step A: Generate Demand & Dispatch packages to drivers
        daily_orders = demand_engine.generate_daily_orders(df_customers, current_date)
        trips_df = dispatch_engine.cluster_orders_into_trips(daily_orders, df_drivers, current_date)

        daily_processed_trips = []
        
        # Step B: Process each unique driver's trip through the physics pipeline
        for trip_id, trip_group in trips_df.groupby('trip_id'):
            # Extract Branch Context
            branch_id = trip_group.iloc[0]['branch_id']
            hub_row = df_branches[df_branches['branch_id'] == branch_id].iloc[0]
            hub_lat, hub_lng = hub_row['lat'], hub_row['lng']
            shift_start_str = config.BRANCH_CONFIGURATIONS[branch_id]['shift_start_time']
            
            # Extract Driver Context
            driver_id = trip_group.iloc[0]['driver_id']
            vehicle_type = df_drivers[df_drivers['driver_id'] == driver_id].iloc[0]['vehicle_type']
            trip_group = trip_group.copy()
            
            # Inject as 'vehicle_type' so Routing Engine can find it. 
            # (Feature Engine will rename it to 'vehicle_type_id' later)
            trip_group['vehicle_type'] = vehicle_type 
            
            # --- The Assembly Line ---
            trip_data = finance_engine.attach_financial_attributes(trip_group)
            trip_data = routing_engine.sequence_trip(trip_data, hub_lat, hub_lng, branch_id)
            trip_data = distance_eta_engine.calculate_google_metrics(trip_data, hub_lat, hub_lng)
            trip_data = weather_engine.apply_weather_to_trip(trip_data, current_date)
            trip_data = state_manager.process_trip_customers(trip_data)
            
            # We MUST run feature_engine because the Physics engine relies on its spatial grid outputs
            trip_data = feature_engine.generate_ml_features(trip_data, current_date, hub_lat, hub_lng)
            
            # The Final Boss: Calculate complex physical delivery times
            trip_data = physics_engine.simulate_times(
                trip_df=trip_data, 
                df_drivers=df_drivers, 
                df_customers=df_customers, 
                current_date=current_date, 
                shift_start_str=shift_start_str
            )
            
            daily_processed_trips.append(trip_data)

        # ==========================================
        # STRIP DOWN TO PRIMITIVE DATA & SAVE BATCH
        # ==========================================
        if daily_processed_trips:
            # Combine all driver trips for the day into one dataframe
            daily_df = pd.concat(daily_processed_trips, ignore_index=True)
            
            # 1. Merge the static floor_number from the customers table
            daily_df = daily_df.merge(df_customers[['customer_id', 'floor_number']], on='customer_id', how='left')
            # Hub return rows won't have a floor number in the customer table, so fill with 0
            daily_df['floor_number'] = daily_df['floor_number'].fillna(0).astype(int)
            
            # 2. Rename columns to strictly match the specific Thesis Schema
            daily_df = daily_df.rename(columns={
                'gps_lat': 'latitude',
                'gps_lng': 'longitude',
                'google_distance_meters': 'google_dist_meters'
            })
            
            # 3. Filter down to ONLY the 20 pure primitive columns 
            final_daily_df = daily_df[final_columns]
            
            # 4. Append directly to the CSV in 'append' mode ('a') to prevent RAM overload.
            # This is why we don't crash when generating 600,000+ rows!
            final_daily_df.to_csv(output_file, mode='a', header=False, index=False)
            
        # Print progress every 50 days to console
        if (day_offset + 1) % 50 == 0 or day_offset == 0:
            elapsed_mins = (time.time() - start_timer) / 60
            print(f"✅ Processed {day_offset + 1}/1500 days... ({elapsed_mins:.1f} mins elapsed)")

    print("="*50)
    print(f"🎉 SIMULATION COMPLETE! 1,500 Days of History Generated.")
    print(f"📂 Master dataset saved to: {output_file}")
    print("="*50)

if __name__ == "__main__":
    run_simulation()