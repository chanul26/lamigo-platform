import math
import random
import httpx
import asyncio
from typing import List, Dict, Tuple, Any

# Securely import the Google Maps API Key from your centralized config
from app.core.config import settings

# ==============================================================================
# 1. Configuration & Constants
# ==============================================================================
EARTH_RADIUS_KM = 6371.0

# 🚨 THE SENSITIVITY DIAL 🚨
# 1.2 means: If the Google Road is 150% longer than a straight bird-flight line, penalize it!
CIRCUITY_THRESHOLD = 2.5 

# Maximum times we allow the algorithm to re-calculate to prevent infinite loops
MAX_PENALTY_LOOPS = 2     

GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY

# ==============================================================================
# 2. Vehicle Mapping
# ==============================================================================
def map_vehicle_to_google_mode(vehicle_type: str) -> str:
    """
    Maps LamiGo's internal VehicleType Enum to Google Routes API travel modes.
    Crucial for getting accurate ETAs (a Lorry takes longer than a Motorcycle).
    """
    mapping = {
        "MOTORCYCLE": "TWO_WHEELER",
        "THREE_WHEEL": "DRIVE", # Tuk-tuks generally follow car traffic rules
        "LORRY": "DRIVE"
    }
    return mapping.get(vehicle_type, "TWO_WHEELER")

# ==============================================================================
# 3. Core Mathematical Functions (Run entirely in RAM - Free & Fast)
# ==============================================================================
def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the straight-line (bird-flight) distance between two GPS points in meters."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c * 1000  # Return in meters

def initial_greedy_route(distance_matrix: Dict[Tuple[str, str], float], start_id: str, waypoint_ids: List[str]) -> List[str]:
    """Nearest Neighbour algorithm to get a fast, mathematically decent starting sequence."""
    unvisited = set(waypoint_ids)
    current = start_id
    route = []
    
    while unvisited:
        next_node = min(unvisited, key=lambda x: distance_matrix[(current, x)])
        route.append(next_node)
        unvisited.remove(next_node)
        current = next_node
        
    return route

def calculate_route_cost(route: List[str], start_id: str, end_id: str, distance_matrix: Dict[Tuple[str, str], float]) -> float:
    """Calculates the total distance of a specific sequence based on the current matrix."""
    if not route: return 0.0
    cost = distance_matrix[(start_id, route[0])]
    for i in range(len(route) - 1):
        cost += distance_matrix[(route[i], route[i+1])]
    cost += distance_matrix[(route[-1], end_id)]
    return cost

def simulated_annealing(waypoints: List[str], start_id: str, end_id: str, distance_matrix: Dict[Tuple[str, str], float]) -> List[str]:
    """
    The Core AI Heuristic Solver. 
    It randomly swaps parts of the route (2-opt) and keeps the sequence if it is shorter.
    It sometimes accepts worse routes early on to escape 'local minima' (dead ends).
    """
    if len(waypoints) <= 2:
        return waypoints # Too small to optimize computationally

    # 1. Start with a greedy baseline
    current_route = initial_greedy_route(distance_matrix, start_id, waypoints)
    current_cost = calculate_route_cost(current_route, start_id, end_id, distance_matrix)
    
    best_route = list(current_route)
    best_cost = current_cost
    
    # SA Parameters (Higher temp = more randomness, lower cooling_rate = slower/more accurate)
    temp = 10000.0
    cooling_rate = 0.995
    min_temp = 1.0
    
    while temp > min_temp:
        # Generate neighbor via 2-opt swap (reverse a sub-segment of the route)
        i, j = sorted(random.sample(range(len(current_route)), 2))
        neighbor_route = current_route[:i] + current_route[i:j+1][::-1] + current_route[j+1:]
        neighbor_cost = calculate_route_cost(neighbor_route, start_id, end_id, distance_matrix)
        
        # Accept if better, or occasionally accept if worse (based on current temperature)
        if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / temp):
            current_route = neighbor_route
            current_cost = neighbor_cost
            
            if current_cost < best_cost:
                best_route = list(current_route)
                best_cost = current_cost
                
        temp *= cooling_rate
        
    return best_route

# ==============================================================================
# 4. External API Integrations
# ==============================================================================
async def fetch_google_route(origin: dict, destination: dict, vehicle_type: str) -> Tuple[int, int, str]:
    """
    Fetches real road distance and duration from Google Routes API.
    Returns: (Distance in meters, Duration in seconds, Source type for logging)
    """
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }
    
    payload = {
        "origin": {"location": {"latLng": {"latitude": origin["lat"], "longitude": origin["lng"]}}},
        "destination": {"location": {"latLng": {"latitude": destination["lat"], "longitude": destination["lng"]}}},
        "travelMode": map_vehicle_to_google_mode(vehicle_type) 
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=5.0)
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                dist = data["routes"][0].get("distanceMeters", 0)
                dur_str = data["routes"][0].get("duration", "0s")
                dur = int(dur_str.replace("s", ""))
                return dist, dur, "API"
        except Exception as e:
            print(f"   ❌ [API ERROR] Google API Failed: {e}")
            
    # --- GRACEFUL FALLBACK ---
    # If Google is down or the API key is expired, the system MUST NOT crash.
    # We estimate the road is 1.5x longer than a straight line.
    fallback_dist = int(calculate_haversine(origin["lat"], origin["lng"], destination["lat"], destination["lng"]) * 1.5)
    speed_kmh = 40 if vehicle_type == "MOTORCYCLE" else 30 # Motorcycles weave through traffic faster
    fallback_eta = int((fallback_dist / (speed_kmh * 1000)) * 3600)
    
    return fallback_dist, fallback_eta, "FALLBACK"

# ==============================================================================
# 5. The Master Orchestrator (The Exposure Point)
# ==============================================================================
async def optimize_trip_sequence(start_node: dict, end_node: dict, waypoints: List[dict], vehicle_type: str) -> List[dict]:
    """
    Takes raw coordinates, runs SA optimization, applies Google Circuity penalties,
    and returns the final ordered payload ready for the ML Engine and Database.
    """
    # --- Telemetry Dashboard Setup ---
    stats = {
        "api_calls_made": 0,
        "cache_hits": 0,
        "penalties_applied": 0,
        "fallbacks_used": 0
    }
    
    print(f"\n⚙️ INITIALIZING LamiGo ROUTING ENGINE for {vehicle_type}...")

    # 1. Map IDs to coordinate dictionaries for instant O(1) lookups
    nodes_map = {start_node["id"]: start_node, end_node["id"]: end_node}
    for wp in waypoints:
        nodes_map[wp["id"]] = wp
        
    all_ids = list(nodes_map.keys())
    waypoint_ids = [wp["id"] for wp in waypoints]
    
    # 2. Build Initial Haversine Distance Matrix (The Flat Earth Assumption)
    print(f"   📐 Calculating base Haversine Matrix for {len(all_ids)} nodes...")
    dist_matrix = {}
    for id1 in all_ids:
        for id2 in all_ids:
            if id1 == id2:
                dist_matrix[(id1, id2)] = 0.0
            else:
                dist_matrix[(id1, id2)] = calculate_haversine(
                    nodes_map[id1]["lat"], nodes_map[id1]["lng"],
                    nodes_map[id2]["lat"], nodes_map[id2]["lng"]
                )

    # In-memory cache to save money on overlapping route segments across different loops
    google_edge_cache = {} 
    
    # Track which loop actually generated the final math
    winning_loop = 1 
    
    # =========================================================================
    # 3. THE CIRCUITY PENALTY LOOP (The "Reality Check")
    # =========================================================================
    for loop in range(MAX_PENALTY_LOOPS):
        current_loop_num = loop + 1
        print(f"\n🔄 --- ROUTING LOOP {current_loop_num}/{MAX_PENALTY_LOOPS} ---")
        
        # Step A: Run Simulated Annealing on current matrix
        best_seq_ids = simulated_annealing(waypoint_ids, start_node["id"], end_node["id"], dist_matrix)
        
        # Step B: Build the full physical journey from Hub -> Stops -> Hub
        full_path_ids = [start_node["id"]] + best_seq_ids + [end_node["id"]]
        
        needs_recalc = False 
        
        # Step C: Check EVERY SINGLE SEGMENT of this proposed route against Google Maps
        for i in range(len(full_path_ids) - 1):
            u = full_path_ids[i]     
            v = full_path_ids[i+1]   
            
            # Helper for clean terminal output (e.g., "pkg_1_unawatuna" -> "UNAWATUNA")
            u_clean = u.split('_')[-1].upper()
            v_clean = v.split('_')[-1].upper()

            # Did we already ask Google about this exact road in a previous loop?
            if (u, v) not in google_edge_cache:
                
                # If not, make the actual API call
                g_dist, g_time, source = await fetch_google_route(nodes_map[u], nodes_map[v], vehicle_type)
                
                # Update Telemetry
                if source == "API":
                    stats["api_calls_made"] += 1
                elif source == "FALLBACK":
                    stats["fallbacks_used"] += 1
                
                print(f"   📡 [FETCH: {source:<8}] {u_clean:<12} -> {v_clean:<12} | Dist: {g_dist}m")

                # Save to cache (INCLUDING the source so the database knows later)
                google_edge_cache[(u, v)] = {"dist": g_dist, "time": g_time, "source": source}
                
                # Look up what the algorithm THOUGHT the distance was (Bird-flight)
                h_dist = dist_matrix[(u, v)]
                circuity_ratio = (g_dist / h_dist) if h_dist > 0 else 0
                
                # --- THE PENALTY APPLICATION ---
                # If the real road is wildly inefficient compared to the bird-flight line...
                if h_dist > 0 and circuity_ratio > CIRCUITY_THRESHOLD:
                    stats["penalties_applied"] += 1
                    
                    print(f"      🚨 [PENALTY] Ratio: {circuity_ratio:.2f}x (Threshold: {CIRCUITY_THRESHOLD}x). Overwriting matrix!")
                    
                    # Force the matrix to use the real road distance, punishing this specific segment
                    dist_matrix[(u, v)] = float(g_dist) 
                    
                    # Tell the system we need to run Simulated Annealing again to fix this
                    needs_recalc = True 
            else:
                # We already checked this exact segment! Free data!
                stats["cache_hits"] += 1
                cached_source = google_edge_cache[(u, v)]["source"]
                print(f"   💾 [CACHE: {cached_source:<8}] {u_clean:<12} -> {v_clean:<12} | Dist: {google_edge_cache[(u,v)]['dist']}m")

        # Step D: Exit Strategy
        if not needs_recalc:
            print("   ✅ Sequence is physically realistic. No penalties needed.")
            winning_loop = current_loop_num
            break 
            
        # If we hit the max allowed loops, we stop to prevent infinite latency and use the current best
        if current_loop_num == MAX_PENALTY_LOOPS:
            winning_loop = current_loop_num
            print(f"   ⚠️ Reached MAX_PENALTY_LOOPS. Forcing exit with Loop {winning_loop} sequence.")

    # =========================================================================
    # 4. End of Run Dashboard & Payload Generation
    # =========================================================================
    print("\n📊 --- ROUTING TELEMETRY DASHBOARD ---")
    print(f"   Total Stops            : {len(waypoints)}")
    print(f"   Winning Sequence       : Derived from Loop {winning_loop}")
    print(f"   Google API Calls Made  : {stats['api_calls_made']}")
    print(f"   Cache Hits (Money Saved): {stats['cache_hits']}")
    print(f"   Fallbacks Used (Errors): {stats['fallbacks_used']}")
    print(f"   Penalties Triggered    : {stats['penalties_applied']}")
    print("--------------------------------------")

    final_output = []
    
    for i, task_id in enumerate(best_seq_ids):
        # Determine the edge that led to this task
        prev_id = start_node["id"] if i == 0 else best_seq_ids[i-1]
        
        # Pull the cached Google Data to send to the ML Model
        edge_data = google_edge_cache.get((prev_id, task_id))
        
        final_output.append({
            "id": task_id,
            "sequence_number": i + 1,
            "google_dist_meters": edge_data["dist"] if edge_data else 0,
            "google_eta_seconds": edge_data["time"] if edge_data else 0,
            "data_source": edge_data["source"] if edge_data else "UNKNOWN" 
        })
        
    return final_output