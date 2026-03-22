import pandas as pd
import datetime
import os
import sys

# ==========================================
# PATH FIX: Ensure Python can find the 'simulator' package
# ==========================================
# This allows you to run `python simulator/test_pipeline.py` from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Local import (config is in the same folder)
import config

# 2. Absolute imports for the sub-folder engines
from simulator.engines import demand_engine, dispatch_engine, routing_engine 
from simulator.engines import distance_eta_engine, weather_engine, finance_engine, feature_engine, physics_engine
from simulator.engines.customer_state_engine import CustomerStateManager

def run_test():
    """
    A single-day test execution of the entire LamiGo digital twin.
    Used for debugging the physics equations and engine handoffs before 
    running the massive 4-year master simulation.
    """
    print("🚀 Booting up the FULL LamiGo Test Pipeline (with Physics!)...")

    # 1. Load the pristine Phase 1 data
    df_customers = pd.read_csv('data/raw/customers.csv')
    df_drivers = pd.read_csv('data/raw/drivers.csv')
    df_branches = pd.read_csv('data/raw/branches.csv')

    # 2. Initialize the State Manager (The Memory)
    state_manager = CustomerStateManager(df_customers)
    
    # 3. Pick a fake simulation date
    # We use May 15th, which triggers the Monsoon season logic in the weather engine!
    test_date = datetime.date(2020, 5, 15) 
    print(f"📅 Simulating Day: {test_date}")

    # ==========================================
    # THE PIPELINE
    # ==========================================
    
    print("📦 Generating Orders & Clustering into Trips...")
    daily_orders = demand_engine.generate_daily_orders(df_customers, test_date)
    trips_df = dispatch_engine.cluster_orders_into_trips(daily_orders, df_drivers, test_date)

    all_processed_trips = []
    
    print("🧠 Running Routing, Baselines, ML Features, and PHYSICS ENGINE...")
    
    # Group the massive dataframe into individual driver trips
    for trip_id, trip_group in trips_df.groupby('trip_id'):
        
        # Get Branch config for the Hub
        branch_id = trip_group.iloc[0]['branch_id']
        hub_row = df_branches[df_branches['branch_id'] == branch_id].iloc[0]
        hub_lat, hub_lng = hub_row['lat'], hub_row['lng']
        shift_start_str = config.BRANCH_CONFIGURATIONS[branch_id]['shift_start_time']
        
        # Merge Driver vehicle info into the trip
        driver_id = trip_group.iloc[0]['driver_id']
        vehicle_type = df_drivers[df_drivers['driver_id'] == driver_id].iloc[0]['vehicle_type']
        trip_group = trip_group.copy()
        
        # Inject vehicle_type for the Routing Engine
        trip_group['vehicle_type'] = vehicle_type
        
        # ==========================================
        # THE ASSEMBLY LINE
        # ==========================================
        # 1. Finance (Assigns COD amounts)
        trip_data = finance_engine.attach_financial_attributes(trip_group)
        # 2. Routing (Solves the Traveling Salesperson Problem)
        trip_data = routing_engine.sequence_trip(trip_data, hub_lat, hub_lng, branch_id)
        # 3. Google Baseline (Calculates Haversine distances and base ETAs)
        trip_data = distance_eta_engine.calculate_google_metrics(trip_data, hub_lat, hub_lng)
        # 4. Weather (Polls the simulated OpenWeather API)
        trip_data = weather_engine.apply_weather_to_trip(trip_data, test_date)
        # 5. Customer State (Customers "learn" to verify their pins over time)
        trip_data = state_manager.process_trip_customers(trip_data)
        # 6. Feature Engine (Calculates H3 grids and spatial/temporal lag features)
        trip_data = feature_engine.generate_ml_features(trip_data, test_date, hub_lat, hub_lng)
        
        # 7. THE FINAL BOSS: PHYSICS ENGINE
        # Calculates the actual delay times based on traffic, weather, cash friction, and fatigue
        trip_data = physics_engine.simulate_times(
            trip_df=trip_data, 
            df_drivers=df_drivers, 
            df_customers=df_customers, 
            current_date=test_date, 
            shift_start_str=shift_start_str
        )
        
        all_processed_trips.append(trip_data)

    # ==========================================
    # EXPORT RESULTS
    # ==========================================
    final_df = pd.concat(all_processed_trips, ignore_index=True)
    
    # Save it inside the simulator graveyard folder to keep the root directory clean
    output_file = 'simulator/temp_debug_pipeline.csv'
    final_df.to_csv(output_file, index=False)
    
    print(f"\n✅ SUCCESS! Processed {len(final_df)} rows.")
    print(f"📂 Saved to '{output_file}'.")
    
    # --- TERMINAL PREVIEW ---
    print("\n⏱️ PREVIEW OF PHYSICS ENGINE OUTPUT (First 5 Stops of a Trip):")
    preview_cols = ['sequence_no', 'customer_id', 'google_eta_seconds', 'actual_time_diff_seconds', 'start_time', 'arrival_time']
    print(final_df[preview_cols].head(5).to_string(index=False))

if __name__ == "__main__":
    run_test()