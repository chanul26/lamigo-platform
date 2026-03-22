import pandas as pd
import numpy as np
import random
from sklearn.cluster import KMeans

def cluster_orders_into_trips(daily_orders_df, df_drivers, current_date):
    """
    Acts as the AI Dispatcher. 
    Groups daily orders into geographic clusters using K-Means so a driver 
    isn't bouncing from the north end of the city to the south end.
    Targets ~60 packages per trip (with moderate variance) for balanced full-day shifts.
    Randomly assigns an available driver to each cluster.
    """
    all_trips = []
    
    # ==========================================
    # REPRODUCIBILITY: DATE-BASED SEEDING
    # ==========================================
    # Convert the date into a unique integer (e.g., 2020-01-01 becomes 737425).
    # This ensures the dispatcher makes the exact same decisions for this day, forever.
    daily_seed = current_date.toordinal()
    np.random.seed(daily_seed)
    random.seed(daily_seed)
    
    # Process each branch independently (Colombo drivers shouldn't deliver in Galle!)
    for branch_id in daily_orders_df['branch_id'].unique():
        
        # 1. Filter data for the current branch
        branch_orders = daily_orders_df[daily_orders_df['branch_id'] == branch_id].copy()
        branch_drivers = df_drivers[df_drivers['branch_id'] == branch_id]
        
        num_orders = len(branch_orders)
        if num_orders == 0:
            continue
            
        # 2. Determine K (How many drivers do we need today?)
        # Target ~60 packages per driver to simulate a balanced 7-8 hour shift.
        # Adding variance (Standard Deviation of 10) means some days the dispatcher 
        # aims for 50 per driver, some days 70+.
        target_packages_per_trip = max(40, int(np.random.normal(loc=60, scale=10)))
        
        # Calculate clusters needed (K = Total Orders / Target Packages per driver)
        k_clusters = max(1, round(num_orders / target_packages_per_trip))
        
        # Safety Check: We can't dispatch more drivers than we actually have working!
        k_clusters = min(k_clusters, len(branch_drivers))
        
        # 3. Randomly select the drivers working this shift
        # replace=False ensures a driver only gets one trip assigned per day.
        # We lock the random_state using our daily_seed so the same drivers work this day.
        working_drivers = branch_drivers.sample(n=k_clusters, replace=False, random_state=daily_seed)['driver_id'].tolist()
        
        # 4. Perform Geographic K-Means Clustering
        # We extract the Lat/Lng coordinates to feed into the ML algorithm
        coordinates = branch_orders[['gps_lat', 'gps_lng']].values
        
        # Initialize and fit K-Means
        # n_init="auto" suppresses a common scikit-learn warning.
        # We lock the random_state here so the geographic cluster borders are identical every run.
        kmeans = KMeans(n_clusters=k_clusters, random_state=daily_seed, n_init="auto")
        branch_orders['cluster_id'] = kmeans.fit_predict(coordinates)
        
        # 5. Assign Clusters to Trips and Drivers
        for cluster_num in range(k_clusters):
            # Get all orders assigned to this specific geographic cluster
            cluster_orders = branch_orders[branch_orders['cluster_id'] == cluster_num].copy()
            
            # K-Means can sometimes create empty clusters if points are extremely dense. Skip if empty.
            if len(cluster_orders) == 0:
                continue
                
            assigned_driver = working_drivers[cluster_num]
            
            # Generate a unique Trip ID (e.g., TRIP_20200101_B_001_D_004)
            # We strip out the hyphens in the date to make it cleaner
            trip_id = f"TRIP_{current_date.strftime('%Y%m%d')}_{branch_id}_{assigned_driver}"
            
            # Append trip and driver info to the orders
            cluster_orders['trip_id'] = trip_id
            cluster_orders['driver_id'] = assigned_driver
            
            all_trips.append(cluster_orders)

    # Combine all branches back into a single dataframe
    final_dispatched_orders = pd.concat(all_trips, ignore_index=True)
    
    # Drop the temporary cluster_id column, we only need trip_id to identify groups now
    final_dispatched_orders = final_dispatched_orders.drop(columns=['cluster_id'])
    
    return final_dispatched_orders