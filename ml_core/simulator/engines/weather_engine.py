import pandas as pd
import numpy as np
import random
import hashlib

def get_daily_rain_probability(current_date):
    """
    Determines the probability of rain based on Sri Lanka's West/South coast monsoon seasons.
    This creates realistic seasonal trends in the data for the ML model to learn.
    """
    month = current_date.month
    
    if month in [5, 6, 9, 10, 11]:
        # Peak Yala Monsoon & Second Inter-monsoon: High chance of heavy rain
        return 0.45
    elif month in [4, 7, 8, 12]:
        # Tailing ends of monsoons / Maha crossover: Moderate chance of rain
        return 0.25
    else:
        # Dry Season (Jan, Feb, Mar): Very low chance of rain
        return 0.08

def apply_weather_to_trip(trip_df, current_date):
    """
    Simulates an OpenWeather API response for a specific trip.
    Applies consistent baseline weather conditions across all stops in the route, 
    with slight micro-variations stop-to-stop to mimic a real API polling.
    """
    # ==========================================
    # REPRODUCIBILITY: TRIP-BASED SEEDING
    # ==========================================
    # We hash the unique 'trip_id' to guarantee that the weather generated 
    # for this specific driver on this specific day is identical every single run.
    trip_id = trip_df.iloc[0]['trip_id']
    trip_seed = int(hashlib.md5(trip_id.encode('utf-8')).hexdigest(), 16) % (2**32)
    random.seed(trip_seed)
    np.random.seed(trip_seed)
    
    # 1. Determine if it rains at all today for this trip
    rain_prob = get_daily_rain_probability(current_date)
    is_raining = random.random() < rain_prob
    
    if not is_raining:
        # 800: Clear sky, 801-804: Clouds
        base_weather_code = random.choice([800, 801, 802, 803, 804])
        base_rain_volume = 0.0
    else:
        # 2. It's raining. Determine the intensity of the storm.
        intensity_roll = random.random()
        
        if intensity_roll < 0.50:
            # 500: Light Rain (0.1mm - 2.5mm per hour)
            base_weather_code = 500
            base_rain_volume = round(random.uniform(0.1, 2.5), 2)
        elif intensity_roll < 0.85:
            # 501: Moderate Rain (2.6mm - 7.5mm per hour)
            base_weather_code = 501
            base_rain_volume = round(random.uniform(2.6, 7.5), 2)
        else:
            # 502: Heavy Rain or 200: Thunderstorm (> 7.5mm per hour)
            base_weather_code = random.choice([502, 200])
            base_rain_volume = round(random.uniform(7.6, 15.0), 2)

    # 3. Apply Weather to Stops
    # To make the data look slightly more "organic" (like a real API polling every 10 mins 
    # as the driver moves across the city), we add a tiny bit of micro-variance to the 
    # rain volume for each stop, but keep the main weather code the same.
    weather_codes = []
    rain_volumes = []
    
    for _ in range(len(trip_df)):
        weather_codes.append(base_weather_code)
        
        if base_rain_volume > 0:
            # +/- 10% fluctuation in rain volume per stop
            fluctuation = np.random.normal(loc=1.0, scale=0.10)
            stop_rain = round(base_rain_volume * fluctuation, 2)
            # Ensure the variance doesn't accidentally drop the volume to 0 during a storm
            rain_volumes.append(max(0.1, stop_rain)) 
        else:
            rain_volumes.append(0.0)
            
    # Append the finalized environmental features to the dataframe
    trip_df['weather_code'] = weather_codes
    trip_df['rain_volume_1h'] = rain_volumes
    
    return trip_df