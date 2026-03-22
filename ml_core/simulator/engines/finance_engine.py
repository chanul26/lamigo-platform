import pandas as pd
import random
import hashlib

def attach_financial_attributes(trip_df):
    """
    Generates realistic Sri Lankan Rupee retail prices for 40% of orders.
    The other 60% are prepaid (0.0).
    Attaches the 'cod_amount' column directly to the trip dataframe.
    """
    cod_amounts = []
    num_orders = len(trip_df)
    
    # ==========================================
    # REPRODUCIBILITY: TRIP-BASED SEEDING
    # ==========================================
    # We hash the unique 'trip_id' to guarantee that the COD amounts 
    # generated for this specific dispatch are identical every time we run the code.
    trip_id = trip_df.iloc[0]['trip_id']
    trip_seed = int(hashlib.md5(trip_id.encode('utf-8')).hexdigest(), 16) % (2**32)
    random.seed(trip_seed)
    
    for _ in range(num_orders):
        if random.random() < 0.40: # 40% chance of being a Cash-On-Delivery (COD) order
            
            # 1. Generate a base price between Rs. 500 and Rs. 15,000
            # triangular(low, high, mode) makes Rs. 1,500 the most common order value,
            # simulating a realistic e-commerce basket size distribution.
            base = int(random.triangular(500, 15000, 1500))
            
            # 2. Apply psychological retail pricing (round down to the nearest 100)
            hundreds_block = (base // 100) * 100 
            
            # Add realistic Sri Lankan retail endings (e.g., 990, 450, 1000)
            retail_ending = random.choice([0, 50, 90, 99]) 
            final_price = hundreds_block + retail_ending
            
            # Safety Check: Ensure the price doesn't drop to zero or negative due to rounding
            if final_price < 100: 
                final_price = random.choice([490, 500, 990])
                
            cod_amounts.append(float(final_price))
        else:
            # Prepaid order (No cash friction at the door)
            cod_amounts.append(0.0)
            
    # Attach the generated financial data to the dataframe
    trip_df['cod_amount'] = cod_amounts
    
    return trip_df