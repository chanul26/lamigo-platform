import pandas as pd
import numpy as np
import random
import hashlib

# ==========================================
# PATH FIX: Point to the new graveyard folder
# ==========================================
from simulator import config

class CustomerStateManager:
    """
    Maintains the evolving state of all 640 customers across the 1,500-day simulation.
    Tracks delivery counts and triggers profile updates (learning) over time.
    """
    def __init__(self, df_customers):
        self.state_db = {}
        
        # Initialize the tracker for all customers
        for _, row in df_customers.iterrows():
            cid = row['customer_id']
            
            # ==========================================
            # REPRODUCIBILITY: CUSTOMER-BASED SEEDING
            # ==========================================
            # Hash the customer_id so their initial "Hidden DNA" is permanent
            cust_seed = int(hashlib.md5(cid.encode('utf-8')).hexdigest(), 16) % (2**32)
            np.random.seed(cust_seed)
            
            # 1. Determine "True DNA" vs "System Profile"
            system_type = row['location_type']
            if system_type == 'OTHER':
                # Assign a hidden reality based on their branch's demographics
                branch_probs = config.BRANCH_CONFIGURATIONS[row['branch_id']]['location_type_probs']
                # We slice the probabilities to exclude 'OTHER' (index 5) and re-normalize
                real_types = config.LOCATION_CHOICES[:-1] 
                real_probs = np.array(branch_probs[:-1])
                real_probs = real_probs / real_probs.sum() 
                
                true_type = np.random.choice(real_types, p=real_probs)
            else:
                # If they aren't 'OTHER', their system profile matches reality
                true_type = system_type
                
            # 2. Determine Learning Threshold
            # We use a normal distribution so some tech-savvy users learn after 50 deliveries, 
            # while stubborn users take 200+ deliveries to update their pins.
            learning_threshold = max(10, int(np.random.normal(loc=200, scale=80)))
            
            # 3. Store in the persistent state dictionary
            self.state_db[cid] = {
                'delivery_count': 0,
                'learning_threshold': learning_threshold,
                'system_verified': row['is_location_verified'],
                'system_location_type': system_type,
                'true_location_type': true_type,
                'sociability_index': row['sociability_index'],
                'payment_readiness': row['payment_readiness']
            }

    def process_trip_customers(self, trip_df):
        """
        Takes a sequenced trip, updates the delivery counts for those customers,
        rolls the dice for profile updates, and attaches the context to the dataframe.
        """
        sys_verified_list = []
        sys_loc_type_list = []
        true_loc_type_list = []
        soc_index_list = []
        pay_readiness_list = []
        
        trip_id = trip_df.iloc[0]['trip_id']
        
        for _, row in trip_df.iterrows():
            cid = row['customer_id']
            
            # ==========================================
            # BYPASS MEMORY FOR THE HUB RETURN
            # ==========================================
            # The Hub is not a human customer. It does not "learn".
            if str(cid).startswith('HUB_'):
                sys_verified_list.append(True)         # Hubs are perfectly mapped
                sys_loc_type_list.append('HUB')        
                true_loc_type_list.append('HUB')       
                soc_index_list.append(0.5)             # Neutral sociability
                pay_readiness_list.append(1.0)         # No cash collected at the end
                continue                               # Skip the rest of the loop

            customer = self.state_db[cid]
            
            # 1. Increment their historical delivery count
            customer['delivery_count'] += 1
            
            # ==========================================
            # REPRODUCIBILITY: EVENT-BASED SEEDING
            # ==========================================
            # Hash the trip_id + customer_id so the outcome of their "learning" roll 
            # is mathematically locked to this specific delivery attempt.
            roll_seed = int(hashlib.md5(f"{trip_id}_{cid}".encode('utf-8')).hexdigest(), 16) % (2**32)
            random.seed(roll_seed)
            
            # 2. Check for Profile Evolution (Learning)
            if customer['delivery_count'] > customer['learning_threshold']:
                
                # Evolution A: Verifying the Pin
                if not customer['system_verified']:
                    if random.random() < 0.50:
                        customer['system_verified'] = True
                
                # Evolution B: Updating Location Type
                # If they verified their pin, they might also fix their profile type
                if customer['system_verified'] and customer['system_location_type'] == 'OTHER':
                    if random.random() < 0.60:
                        customer['system_location_type'] = customer['true_location_type']
            
            # 3. Append the current state to the lists for this trip
            sys_verified_list.append(customer['system_verified'])
            sys_loc_type_list.append(customer['system_location_type'])
            true_loc_type_list.append(customer['true_location_type'])
            soc_index_list.append(customer['sociability_index'])
            pay_readiness_list.append(customer['payment_readiness'])
            
        # 4. Attach the data back to the trip dataframe
        trip_df['is_pin_verified'] = sys_verified_list
        trip_df['location_type'] = sys_loc_type_list      
        trip_df['true_location_type'] = true_loc_type_list 
        trip_df['sociability_index'] = soc_index_list      
        trip_df['payment_readiness'] = pay_readiness_list  
        
        return trip_df