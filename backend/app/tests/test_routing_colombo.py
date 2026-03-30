import pytest
import time
import random
import math
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

# Import the core engine orchestrator
from app.services.routing_service import optimize_trip_sequence

# ==============================================================================
# HELPER UTILITIES FOR THE VISUAL TEST
# ==============================================================================

def calculate_simple_dist(p1: Dict, p2: Dict) -> float:
    """Calculates basic Euclidean distance for the greedy visualizer."""
    return math.sqrt((p1['lat'] - p2['lat'])**2 + (p1['lng'] - p2['lng'])**2)

def get_greedy_sequence(start_node: Dict, waypoints: List[Dict]) -> List[Dict]:
    """
    Simulates a standard 'Nearest Neighbor' algorithm.
    This represents what a basic, non-AI logistics system would produce.
    """
    unvisited = list(waypoints)
    current = start_node
    greedy_path = []
    
    while unvisited:
        # Find the geographically closest next stop
        next_node = min(unvisited, key=lambda x: calculate_simple_dist(current, x))
        greedy_path.append(next_node)
        unvisited.remove(next_node)
        current = next_node
        
    return greedy_path

# ==============================================================================
# MAIN TEST CASE
# ==============================================================================

@pytest.mark.asyncio
async def test_lamigo_colombo_comparison_visual():
    """
    COMPARISON TEST: 
    1. Generates a 'Naive' Greedy route.
    2. Runs the full LamiGo Optimization.
    3. Plots both side-by-side to show the optimization 'win'.
    """
    print("\n\n" + "="*60)
    print("🚀 STARTING COLOMBO VISUAL COMPARISON: GREEDY VS. OPTIMIZED")
    print("="*60)

    # --- STEP 1: Setup Colombo Environment ---
    # Central Hub near Colombo Fort
    start_node = {"id": "hub_fort", "lat": 6.9344, "lng": 79.8428}
    
    # Generate 60 Random Waypoints within the Colombo city bounding box
    random.seed(42) # Locked seed for consistent debugging
    waypoints = []
    for i in range(1, 61):
        waypoints.append({
            "id": f"task_{i}",
            "lat": round(random.uniform(6.8700, 6.9600), 6),
            "lng": round(random.uniform(79.8500, 79.9100), 6)
        })

    # --- STEP 2: Calculate the 'Naive' Greedy Route (The Baseline) ---
    # This happens instantly in RAM
    greedy_seq = get_greedy_sequence(start_node, waypoints)

    # --- STEP 3: Run the LamiGo Master Orchestrator (The AI Result) ---
    # This includes Simulated Annealing + Google Road Penalties
    start_time = time.time()
    optimized_payload = await optimize_trip_sequence(
        start_node=start_node,
        end_node=start_node, # Return to same hub
        waypoints=waypoints,
        vehicle_type="MOTORCYCLE"
    )
    exec_duration = time.time() - start_time

    # Map the IDs back to coordinates for plotting the final result
    wp_map = {wp["id"]: wp for wp in waypoints}
    optimized_seq = [wp_map[item["id"]] for item in optimized_payload]

    # --- STEP 4: Visualization (Two-Pane Plot) ---
    # We create a figure with two subplots (1 row, 2 columns)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # -- PLOT 1: THE GREEDY (NAIVE) PATH --
    # Build coordinates including the return trip
    g_lats = [start_node["lat"]] + [w["lat"] for w in greedy_seq] + [start_node["lat"]]
    g_lngs = [start_node["lng"]] + [w["lng"] for w in greedy_seq] + [start_node["lng"]]
    
    ax1.plot(g_lngs, g_lats, color='#94a3b8', linestyle='--', alpha=0.6, label="Naive Path")
    ax1.scatter(g_lngs, g_lats, c='#64748b', s=20)
    ax1.plot(start_node["lng"], start_node["lat"], 'rs', markersize=12, label="Hub")
    ax1.set_title("1. INITIAL GREEDY (Nearest Neighbor)\nOften results in line-crossings and backtracking", fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # -- PLOT 2: THE FINAL OPTIMIZED PATH --
    # Build coordinates including the return trip
    o_lats = [start_node["lat"]] + [w["lat"] for w in optimized_seq] + [start_node["lat"]]
    o_lngs = [start_node["lng"]] + [w["lng"] for w in optimized_seq] + [start_node["lng"]]
    
    ax2.plot(o_lngs, o_lats, color='#0ea5e9', linewidth=2.5, label="Optimized Path")
    ax2.scatter(o_lngs, o_lats, c='#0284c7', s=30)
    ax2.plot(start_node["lng"], start_node["lat"], 'rs', markersize=12, label="Hub")
    ax2.set_title(f"2. FINAL LAMIGO OPTIMIZED\nCalculated in {exec_duration:.2f}s | Real-World Verified", fontsize=14, fontweight='bold', color='#0369a1')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # Final visual polish
    plt.suptitle("LamiGo Routing Optimization: Colombo Stress Test (60 Stops)", fontsize=18, y=0.98, fontweight='extra bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    print(f"\n✅ Comparison complete. Displaying visual plots...")
    plt.show()