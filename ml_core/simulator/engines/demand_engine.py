import pandas as pd
import numpy as np

def generate_daily_orders(df_customers, current_date):
    """
    Simulates daily delivery demand across all branches.
    Targets a mean of ~400 total orders across the 640 customer base,
    using a Normal Distribution for realistic day-to-day variance.
    """
    daily_orders = []
    
    # ==========================================
    # REPRODUCIBILITY: DATE-BASED SEEDING
    # ==========================================
    # By converting the date to a unique integer (ordinal), we ensure that 
    # '2020-05-15' always generates the exact same volume and picks the 
    # exact same customers, making the simulation 100% deterministic.
    daily_seed = current_date.toordinal()
    np.random.seed(daily_seed)
    
    # 1. Temporal ML Feature: Weekend Volume Drop
    # Weekends (Saturday=5, Sunday=6) generally have 15% less B2C delivery volume.
    is_weekend = current_date.weekday() >= 5
    volume_multiplier = 0.85 if is_weekend else 1.0
    
    # 2. Process each branch independently
    for branch_id in df_customers['branch_id'].unique():
        
        # Isolate the customer pool for this specific branch
        branch_customers = df_customers[df_customers['branch_id'] == branch_id]
        max_customers = len(branch_customers)
        
        # 3. Calculate Target Volume
        # To hit 400 total out of 640, each branch needs ~62.5% of its base active.
        base_mean = max_customers * 0.625 
        mean_volume = base_mean * volume_multiplier
        
        # Set the variance (Standard Deviation) to 12% of the mean.
        # This creates the natural swing (e.g., some days Colombo has 200 orders, some days 250)
        std_dev = mean_volume * 0.12 
        
        # 4. Roll the Dice (Normal Distribution)
        today_volume = int(np.random.normal(loc=mean_volume, scale=std_dev))
        
        # Safety Constraint: Cannot have fewer than 1 order, or more orders than total customers
        today_volume = max(1, min(today_volume, max_customers))
        
        # 5. Sample the Customers
        # replace=False ensures a customer gets a maximum of 1 delivery per day.
        # We pass our daily_seed to the pandas random_state so the customer selection is also reproducible!
        sampled_customers = branch_customers.sample(n=today_volume, replace=False, random_state=daily_seed)
        
        # 6. Build the Order Records
        for _, customer in sampled_customers.iterrows():
            daily_orders.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "branch_id": branch_id,
                "customer_id": customer['customer_id'],
                "gps_lat": customer['gps_lat'],
                "gps_lng": customer['gps_lng']
            })
            
    return pd.DataFrame(daily_orders)