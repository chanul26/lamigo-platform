import pandas as pd
import numpy as np
import math

# ==========================================
# HELPER 1: GEOGRAPHIC MATH
# ==========================================
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the straight-line distance between two GPS points on Earth in meters.
    Because the Earth is a sphere, we cannot use simple Pythagorean geometry.
    """
    R = 6371000  # Radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def calculate_distance_matrix(coords):
    """
    Creates an NxN grid (matrix) of distances between all points (including the Hub).
    If a driver has 60 stops, this creates a 61x61 matrix so the algorithm 
    instantly knows the distance from any stop to any other stop.
    """
    n = len(coords)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i][j] = haversine_distance(
                    coords[i][0], coords[i][1], 
                    coords[j][0], coords[j][1]
                )
    return dist_matrix

# ==========================================
# ROUTING ALGORITHMS
# ==========================================
def nearest_neighbor(dist_matrix):
    """
    STEP 1: The Greedy Approach.
    Generates an initial route starting from the Hub (Node 0).
    The driver simply goes to the closest unvisited location, over and over.
    This is fast, but often creates overlapping, messy routes at the end.
    """
    num_nodes = len(dist_matrix)
    unvisited = set(range(1, num_nodes))
    route = [0]  # Start at the Hub (always index 0)
    current_node = 0
    
    while unvisited:
        # Find the absolute closest neighbor that hasn't been visited yet
        next_node = min(unvisited, key=lambda x: dist_matrix[current_node][x])
        route.append(next_node)
        unvisited.remove(next_node)
        current_node = next_node
        
    return route

def two_opt_swap(route, dist_matrix, max_passes=5):
    """
    STEP 2: Route Refinement (Untangling the string).
    Refines the Nearest Neighbor route by finding and removing crossed paths. 
    It takes a segment of the route, reverses it, and checks if the total 
    distance drops. If it does, it keeps the new un-crossed route.
    """
    def route_distance(rt):
        # Calculates the total meters driven for a proposed route
        return sum(dist_matrix[rt[i]][rt[i+1]] for i in range(len(rt)-1))
    
    best_route = route
    best_distance = route_distance(best_route)
    
    improvement = True
    passes = 0
    
    # Keep optimizing until we can't find any more shortcuts, or we hit max passes
    while improvement and passes < max_passes:
        improvement = False
        passes += 1
        for i in range(1, len(best_route) - 1):
            for j in range(i + 1, len(best_route)):
                
                # Perform a 2-opt swap (reverse the delivery order between stop i and stop j)
                new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                new_distance = route_distance(new_route)
                
                # If the swap made the route shorter, keep it!
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improvement = True
                    break # Break out to restart the search with the newly optimized route
            if improvement:
                break
                
    return best_route

# ==========================================
# MAIN ENGINE FUNCTION
# ==========================================
def sequence_trip(trip_df, hub_lat, hub_lng, branch_id):
    """
    The orchestrator. Takes an unsorted batch of packages, applies the routing 
    algorithms to find the most efficient sequence, and then appends a final 
    "Return to Hub" row so the driver's shift ends correctly.
    """
    # 1. Prepare coordinates: Hub is always index 0, deliveries are 1 to N
    deliveries = trip_df.to_dict('records')
    coords = [(hub_lat, hub_lng)] + [(row['gps_lat'], row['gps_lng']) for row in deliveries]
    
    # 2. Build Distance Matrix & Optimize
    dist_matrix = calculate_distance_matrix(coords)
    nn_route = nearest_neighbor(dist_matrix)          # Get a fast initial guess
    optimal_route = two_opt_swap(nn_route, dist_matrix) # Untangle the route
    
    # 3. Reorder the actual DataFrame based on the optimal route
    # (We subtract 1 because index 0 was the Hub, which isn't in the dataframe yet)
    delivery_order = [node_idx - 1 for node_idx in optimal_route[1:]]
    trip_df = trip_df.iloc[delivery_order].copy()
    
    # 4. Assign the official sequence number for the deliveries (1 to N)
    trip_df['sequence_no'] = range(1, len(trip_df) + 1)
    
    # ==========================================
    # LOGIC: THE HUB RETURN
    # ==========================================
    # We must explicitly add a row telling the driver to drive back to the warehouse 
    # to drop off cash and un-delivered items.
    final_sequence_no = len(trip_df) + 1
    
    hub_return_row = {
        'date': trip_df.iloc[0]['date'],           
        'trip_id': trip_df.iloc[0]['trip_id'],
        'driver_id': trip_df.iloc[0]['driver_id'],
        'branch_id': branch_id,
        'customer_id': f"HUB_{branch_id}",         # Unique ID so the model knows it's the Hub
        'gps_lat': hub_lat,
        'gps_lng': hub_lng,
        'location_type': 'HUB',                    
        'is_pin_verified': True,                   # The Hub's pin is always perfect
        'sequence_no': final_sequence_no,
        'vehicle_type': trip_df.iloc[0]['vehicle_type']
    }
    
    # Append the Hub return row to the bottom of the trip
    hub_df = pd.DataFrame([hub_return_row])
    
    # Use pd.concat (modern pandas standard) instead of the deprecated append()
    trip_df = pd.concat([trip_df, hub_df], ignore_index=True)
    
    return trip_df