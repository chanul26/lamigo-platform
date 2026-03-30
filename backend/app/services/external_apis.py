import random
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from app.core.config import settings

# ==============================================================================
# 1. Configuration & Constants
# ==============================================================================
SERVICE_TIME_SECONDS = 600  # 10 minutes at the door
GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY

def map_vehicle_to_google_mode(vehicle_type: str) -> str:
    mapping = {
        "MOTORCYCLE": "TWO_WHEELER",
        "THREE_WHEEL": "DRIVE", 
        "LORRY": "DRIVE"
    }
    return mapping.get(vehicle_type, "TWO_WHEELER")

# ==============================================================================
# 2. External API Callers (Weather & Traffic)
# ==============================================================================

async def fetch_weather_for_timestamp(lat: float, lng: float, target_time: datetime) -> Dict[str, Any]:
    """
    Mocked OpenWeather API (since the real API is currently inaccessible).
    Generates realistic Sri Lankan weather based on the hour.
    """
    await asyncio.sleep(0.01) # Simulate network ping
    hour = target_time.hour
    
    base_temp = 32.0 if 12 <= hour <= 16 else 29.0 if 7 <= hour <= 18 else 25.0
    actual_temp = round(base_temp + random.uniform(-1.0, 1.0), 1)

    if 14 <= hour <= 18 and random.random() < 0.6: 
        weather_code, rain_volume = 501, round(random.uniform(2.0, 15.0), 2)
    elif random.random() < 0.15:
        weather_code, rain_volume = 500, round(random.uniform(0.1, 1.9), 2)
    else:
        weather_code, rain_volume = 800, 0.0

    return {"weather_code": weather_code, "rain_volume_1h": rain_volume, "temperature_c": actual_temp}

async def fetch_google_route_with_traffic(origin: dict, destination: dict, vehicle_type: str, departure_time: datetime) -> Tuple[int, int]:
    """
    Queries Google Routes API with a specific future departure time.
    This guarantees we get the exact traffic multiplier for that specific hour.
    """
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }
    
    # Format datetime to RFC3339 UTC exactly as Google expects it (e.g., "2024-10-15T15:01:23Z")
    formatted_time = departure_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    payload = {
        "origin": {"location": {"latLng": {"latitude": origin["lat"], "longitude": origin["lng"]}}},
        "destination": {"location": {"latLng": {"latitude": destination["lat"], "longitude": destination["lng"]}}},
        "travelMode": map_vehicle_to_google_mode(vehicle_type),
        "departureTime": formatted_time, # ✨ THE MAGIC BULLET: Future Traffic Calculation
        "routingPreference": "TRAFFIC_AWARE" # Force Google to use live/historical traffic models
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=5.0)
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                dist = data["routes"][0].get("distanceMeters", 0)
                dur_str = data["routes"][0].get("duration", "0s")
                dur = int(dur_str.replace("s", ""))
                return dist, dur
        except Exception as e:
            print(f"   ❌ [TRAFFIC API ERROR]: {e}")
            
    # Fallback if Google fails
    return 0, 0

# ==============================================================================
# 3. The Cumulative Timeline Builder
# ==============================================================================

async def build_delivery_timeline(
    route_sequence: List[Dict], 
    scheduled_start_time: datetime,
    waypoints_data: Dict[str, Dict], # Full dictionary of {id: {lat, lng}} 
    start_node: Dict,                # Need the Hub coordinates to calculate the very first drive
    vehicle_type: str
) -> List[Dict]:
    """
    Re-evaluates the static route using live Google Traffic and Mocked Weather.
    """
    enriched_timeline = []
    
    # 1. Initialize the clock and physical location
    current_simulated_time = scheduled_start_time
    current_location = start_node
    
    for step in route_sequence:
        task_id = step["id"]
        target_location = waypoints_data.get(task_id, start_node)
        
        # 2. Add Service Time BEFORE driving (unless it's the very first stop leaving the hub)
        if step["sequence_number"] > 1:
            current_simulated_time += timedelta(seconds=SERVICE_TIME_SECONDS)
            
        departure_time = current_simulated_time
        
        # 3. 📡 LIVE GOOGLE TRAFFIC CALL: Fetch ETA for this specific departure time
        actual_dist, traffic_eta = await fetch_google_route_with_traffic(
            origin=current_location,
            destination=target_location,
            vehicle_type=vehicle_type,
            departure_time=departure_time
        )
        
        # If Google failed, fall back to the old static ETA from the routing loop
        final_eta = traffic_eta if traffic_eta > 0 else step["google_eta_seconds"]
        final_dist = actual_dist if actual_dist > 0 else step["google_dist_meters"]

        # 4. Advance the clock by the actual driving time
        current_simulated_time += timedelta(seconds=final_eta)
        arrival_time = current_simulated_time
        
        # 5. Fetch Weather for the Arrival
        weather_data = await fetch_weather_for_timestamp(
            lat=target_location["lat"], 
            lng=target_location["lng"], 
            target_time=arrival_time
        )
        
        # 6. Build the ML Payload
        enriched_step = {
            "id": task_id,
            "sequence_number": step["sequence_number"],
            "is_return_leg": step.get("is_return_leg", False),
            
            # The newly updated Traffic-Aware Google data
            "google_dist_meters": final_dist,
            "google_eta_seconds": final_eta,
            
            # Temporal Data
            "estimated_arrival_time": arrival_time,
            "hour_of_day": arrival_time.hour,
            
            # Weather Data
            "weather_code": weather_data["weather_code"],
            "rain_volume_1h": weather_data["rain_volume_1h"],
            "temperature_c": weather_data["temperature_c"]
        }
        
        enriched_timeline.append(enriched_step)
        
        # 7. Update current location for the next loop iteration
        current_location = target_location
            
    return enriched_timeline