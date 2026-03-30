import math
import random
import httpx
import asyncio
from typing import List, Dict, Tuple, Any

# Securely import the Google Maps API Key from your centralized config
# This ensures sensitive keys are never hardcoded in the logic
from app.core.config import settings

# ==============================================================================
# 1. Configuration & Constants
# ==============================================================================
EARTH_RADIUS_KM = 6371.0

# 🚨 THE SENSITIVITY DIAL (Circuity Factor)
# This acts as a 'BS-detector' for straight-line math.
# 2.5 means: If the real road distance is > 2.5x the bird-flight distance, 
# the system flags that segment as physically complex (e.g., rivers, mountains).
CIRCUITY_THRESHOLD = 2.5 

# Prevents the system from looping indefinitely if it keeps finding bad roads.
# 2 loops is the sweet spot for balance between accuracy and API latency.
MAX_PENALTY_LOOPS = 2     

GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY

# ==============================================================================
# 2. Vehicle Mapping
# ==============================================================================
def map_vehicle_to_google_mode(vehicle_type: str) -> str:
    """
    Translates LamiGo internal vehicle types to Google's accepted travel modes.
    Google uses TWO_WHEELER for motorcycles and DRIVE for cars/trucks.
    """
    mapping = {
        "MOTORCYCLE": "TWO_WHEELER",
        "THREE_WHEEL": "DRIVE", # Tuk-tuks generally follow car traffic rules/speeds
        "LORRY": "DRIVE"
    }
    return mapping.get(vehicle_type, "TWO_WHEELER")

# ==============================================================================
# 3. Core Mathematical Functions (Run in RAM - Zero Cost & High Speed)
# ==============================================================================
def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the bird-flight distance between two GPS points using spherical trigonometry.
    Essential for building the initial 'guess' matrix before calling expensive APIs.
    """
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    # The 'a' value represents the square of half the chord length between the points
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    # 'c' is the angular distance in radians
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c * 1000  # Result converted to meters

def initial_greedy_route(distance_matrix: Dict[Tuple[str, str], float], start_id: str, waypoint_ids: List[str]) -> List[str]:
    """
    A 'Nearest Neighbor' algorithm. It builds a path by always picking the closest unvisited stop.
    Provides a solid 'baseline' sequence for the AI to start optimizing from.
    """
    unvisited = set(waypoint_ids)
    current = start_id
    route = []
    
    while unvisited:
        # Find the node with the minimum distance from the current position
        next_node = min(unvisited, key=lambda x: distance_matrix[(current, x)])
        route.append(next_node)
        unvisited.remove(next_node)
        current = next_node
        
    return route

def calculate_route_cost(route: List[str], start_id: str, end_id: str, distance_matrix: Dict[Tuple[str, str], float]) -> float:
    """Calculates the total distance of a proposed sequence, including the return to Hub."""
    if not route: return 0.0
    # Segment 1: Hub to first stop
    cost = distance_matrix[(start_id, route[0])]
    # Segment 2: All connections between stops
    for i in range(len(route) - 1):
        cost += distance_matrix[(route[i], route[i+1])]
    # Segment 3: Last stop back to Hub
    cost += distance_matrix[(route[-1], end_id)]
    return cost

def simulated_annealing(waypoints: List[str], start_id: str, end_id: str, distance_matrix: Dict[Tuple[str, str], float]) -> List[str]:
    """
    THE AI SOLVER: Inspired by metallurgy (heating/cooling metal).
    It explores millions of possible routes to find the shortest one without 
    checking every single combination (which would be trillions for 60 stops).
    """
    if len(waypoints) <= 2:
        return waypoints 

    # 1. Start with the Greedy baseline
    current_route = initial_greedy_route(distance_matrix, start_id, waypoints)
    current_cost = calculate_route_cost(current_route, start_id, end_id, distance_matrix)
    
    best_route = list(current_route)
    best_cost = current_cost
    
    # SA Parameters: 100k temp with 0.9999 cooling is optimized for 60+ nodes (High Accuracy)
    temp = 100000.0
    cooling_rate = 0.9999
    min_temp = 0.01
    
    while temp > min_temp:
        # 2. GENERATE NEIGHBOR: Perform a '2-opt' swap (reverses a random chunk of the route)
        # This is the primary way the AI 'uncrosses' lines on a map.
        i, j = sorted(random.sample(range(len(current_route)), 2))
        neighbor_route = current_route[:i] + current_route[i:j+1][::-1] + current_route[j+1:]
        neighbor_cost = calculate_route_cost(neighbor_route, start_id, end_id, distance_matrix)
        
        # 3. ACCEPTANCE LOGIC:
        # If the new route is better, take it. 
        # If it's worse, MAYBE take it based on the current 'heat' to escape dead-ends (local minima).
        if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / temp):
            current_route = neighbor_route
            current_cost = neighbor_cost
            
            # Keep track of the absolute best we've seen so far
            if current_cost < best_cost:
                best_route = list(current_route)
                best_cost = current_cost
                
        # 4. COOL DOWN: Reduce randomness as we get closer to the solution
        temp *= cooling_rate
        
    return best_route

# ==============================================================================
# 4. External API Integrations
# ==============================================================================
async def fetch_google_route(origin: dict, destination: dict, vehicle_type: str) -> Tuple[int, int, str]:
    """
    Communicates with Google Routes V2 API to get real-world driving data.
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
                # Google returns duration as a string like '1200s'
                dur_str = data["routes"][0].get("duration", "0s")
                dur = int(dur_str.replace("s", ""))
                return dist, dur, "API"
        except Exception as e:
            print(f"   ❌ [API ERROR] Google API Failed: {e}")
            
    # --- GRACEFUL FALLBACK ---
    # Ensures the system never crashes if Google is down or the internet is spotty.
    fallback_dist = int(calculate_haversine(origin["lat"], origin["lng"], destination["lat"], destination["lng"]) * 1.5)
    speed_kmh = 40 if vehicle_type == "MOTORCYCLE" else 30 
    fallback_eta = int((fallback_dist / (speed_kmh * 1000)) * 3600)
    
    return fallback_dist, fallback_eta, "FALLBACK"

# ==============================================================================
# 5. The Master Orchestrator (The Exposure Point)
# ==============================================================================
async def optimize_trip_sequence(start_node: dict, end_node: dict, waypoints: List[dict], vehicle_type: str) -> List[dict]:
    """
    The main entry point. Orchestrates the flow between math, AI, and APIs.
    """
    # Initialize telemetry trackers for performance auditing
    stats = {
        "api_calls_made": 0,
        "cache_hits": 0,
        "penalties_applied": 0,
        "fallbacks_used": 0
    }
    
    print(f"\n⚙️ INITIALIZING LamiGo ROUTING ENGINE for {vehicle_type}...")

    # Index nodes for O(1) coordinate lookup during the loops
    nodes_map = {start_node["id"]: start_node, end_node["id"]: end_node}
    for wp in waypoints:
        nodes_map[wp["id"]] = wp
        
    all_ids = list(nodes_map.keys())
    waypoint_ids = [wp["id"] for wp in waypoints]
    
    # 📐 INITIAL MATRIX: Build the first world-view using cheap Haversine math
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

    # Cache prevents paying for the same road twice if the algorithm revisits it
    google_edge_cache = {} 
    
    # Track the absolute best physical sequence across different loop iterations
    best_overall_sequence = []
    best_overall_google_dist = float('inf') 
    winning_loop = 1 
    
    # =========================================================================
    # 3. THE CIRCUITY PENALTY LOOP (Reality Correction)
    # =========================================================================
    for loop in range(MAX_PENALTY_LOOPS):
        current_loop_num = loop + 1
        print(f"\n🔄 --- ROUTING LOOP {current_loop_num}/{MAX_PENALTY_LOOPS} ---")
        
        # Step A: Run AI Optimization on the CURRENT matrix
        current_seq_ids = simulated_annealing(waypoint_ids, start_node["id"], end_node["id"], dist_matrix)
        
        # Step B: Build the full path (Hub -> Stops -> Hub)
        full_path_ids = [start_node["id"]] + current_seq_ids + [end_node["id"]]
        
        needs_recalc = False 
        current_loop_total_google_dist = 0 
        
        # Step C: REALITY CHECK - Verify every segment of the AI path with Google
        for i in range(len(full_path_ids) - 1):
            u = full_path_ids[i]     
            v = full_path_ids[i+1]   
            u_clean, v_clean = u.split('_')[-1].upper(), v.split('_')[-1].upper()

            # 1. Fetch from Cache or API
            if (u, v) not in google_edge_cache:
                g_dist, g_time, source = await fetch_google_route(nodes_map[u], nodes_map[v], vehicle_type)
                if source == "API": stats["api_calls_made"] += 1
                elif source == "FALLBACK": stats["fallbacks_used"] += 1
                print(f"   📡 [FETCH: {source:<8}] {u_clean:<12} -> {v_clean:<12} | Dist: {g_dist}m")
                google_edge_cache[(u, v)] = {"dist": g_dist, "time": g_time, "source": source}
            else:
                stats["cache_hits"] += 1
                g_dist = google_edge_cache[(u, v)]["dist"]
                print(f"   💾 [CACHE: {google_edge_cache[(u,v)]['source']:<8}] {u_clean:<12} -> {v_clean:<12} | Dist: {g_dist}m")

            current_loop_total_google_dist += g_dist

            # 2. Check for Circuity (Road vs. Flight)
            h_dist = dist_matrix[(u, v)]
            circuity_ratio = (g_dist / h_dist) if h_dist > 0 else 0
            
            if h_dist > 0 and circuity_ratio > CIRCUITY_THRESHOLD:
                stats["penalties_applied"] += 1
                print(f"      🚨 [PENALTY] Ratio: {circuity_ratio:.2f}x. Correcting matrix!")
                # Overwrite the matrix with the real-world distance to punish this segment
                dist_matrix[(u, v)] = float(g_dist) 
                needs_recalc = True 

        # Step D: COMPETITIVE EVALUATION
        # If this loop's real-world distance is better than anything we've seen, it's the new leader.
        print(f"   📏 Loop {current_loop_num} Real-World Distance: {current_loop_total_google_dist / 1000:.2f} km")
        if current_loop_total_google_dist < best_overall_google_dist:
            best_overall_google_dist = current_loop_total_google_dist
            best_overall_sequence = current_seq_ids
            winning_loop = current_loop_num

        # Step E: Exit Strategy
        if not needs_recalc:
            print("   ✅ Sequence is physically realistic. Optimization complete.")
            break 
            
        if current_loop_num == MAX_PENALTY_LOOPS:
            print(f"   ⚠️ Reached MAX_PENALTY_LOOPS. Exiting.")

    # =========================================================================
    # 4. Final Telemetry & Payload Generation
    # =========================================================================
    print("\n📊 --- ROUTING TELEMETRY DASHBOARD ---")
    print(f"   Total Stops            : {len(waypoints)}")
    print(f"   Winning Sequence       : Derived from Loop {winning_loop} ({best_overall_google_dist / 1000:.2f} km)")
    print(f"   Google API Calls Made  : {stats['api_calls_made']}")
    print(f"   Cache Hits (Money Saved): {stats['cache_hits']}")
    print(f"   Fallbacks Used (Errors): {stats['fallbacks_used']}")
    print(f"   Penalties Triggered    : {stats['penalties_applied']}")
    print("--------------------------------------")

    final_output = []
    
    # 1. Output the Standard Delivery Tasks
    for i, task_id in enumerate(best_overall_sequence):
        prev_id = start_node["id"] if i == 0 else best_overall_sequence[i-1]
        edge_data = google_edge_cache.get((prev_id, task_id))
        
        final_output.append({
            "id": task_id,
            "sequence_number": i + 1,
            "google_dist_meters": edge_data["dist"] if edge_data else 0,
            "google_eta_seconds": edge_data["time"] if edge_data else 0,
            "data_source": edge_data["source"] if edge_data else "UNKNOWN",
            "is_return_leg": False # Flag telling the API layer to add Service Time here
        })
        
    # ✨ 2. Output the Final Return-to-Hub Segment
    # This is critical for predicting Trip.estimated_return_time_scheduled in the database
    last_task_id = best_overall_sequence[-1]
    return_edge_data = google_edge_cache.get((last_task_id, end_node["id"]))
    
    final_output.append({
        "id": end_node["id"], # Typically the Branch/Hub ID
        "sequence_number": len(best_overall_sequence) + 1,
        "google_dist_meters": return_edge_data["dist"] if return_edge_data else 0,
        "google_eta_seconds": return_edge_data["time"] if return_edge_data else 0,
        "data_source": return_edge_data["source"] if return_edge_data else "UNKNOWN",
        "is_return_leg": True # Tells the API layer NOT to add 10 mins service time here
    })
        
    return final_output