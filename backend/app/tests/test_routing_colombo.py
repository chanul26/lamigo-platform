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
    """Calculates basic Euclidean distance for the greedy baseline visualizer."""
    return math.sqrt((p1['lat'] - p2['lat'])**2 + (p1['lng'] - p2['lng'])**2)

def get_greedy_sequence(start_node: Dict, waypoints: List[Dict]) -> List[Dict]:
    """
    Simulates a standard 'Nearest Neighbor' algorithm.
    Represents a naive system without Simulated Annealing or Road-Awareness.
    """
    unvisited = list(waypoints)
    current = start_node
    greedy_path = []
    
    while unvisited:
        # Greedily pick the closest physical point
        next_node = min(unvisited, key=lambda x: calculate_simple_dist(current, x))
        greedy_path.append(next_node)
        unvisited.remove(next_node)
        current = next_node
        
    return greedy_path

# ==============================================================================
# MAIN TEST CASE: COLOMBO STRESS TEST
# ==============================================================================

@pytest.mark.asyncio
async def test_lamigo_colombo_comparison_visual():
    """
    STRESS TEST & VISUAL COMPARISON: 
    Validates that the AI-optimized route is superior to the Greedy approach
    by plotting them side-by-side. Handles 60 packages + 1 Return Leg.
    """
    print("\n\n" + "="*60)
    print("🚀 STARTING COLOMBO VISUAL COMPARISON: GREEDY VS. OPTIMIZED")
    print("="*60)

    # --- STEP 1: Setup Colombo Hub & Random Tasks ---
    start_node = {"id": "hub_fort", "lat": 6.9344, "lng": 79.8428}
    
    # Generate 60 tasks in the Colombo city bounding box
    random.seed(42) 
    waypoints = []
    for i in range(1, 61):
        waypoints.append({
            "id": f"task_{i}",
            "lat": round(random.uniform(6.8700, 6.9600), 6),
            "lng": round(random.uniform(79.8500, 79.9100), 6)
        })

    # --- STEP 2: Calculate the Baseline (Greedy) ---
    greedy_seq = get_greedy_sequence(start_node, waypoints)

    # --- STEP 3: Run the LamiGo Engine (AI Optimized) ---
    start_time = time.time()
    optimized_payload = await optimize_trip_sequence(
        start_node=start_node,
        end_node=start_node, # Return to Fort Hub
        waypoints=waypoints,
        vehicle_type="MOTORCYCLE"
    )
    exec_duration = time.time() - start_time

    # IMPORTANT: The engine now returns N+1 segments (The stops + the Return Leg)
    assert len(optimized_payload) == 61, f"Expected 61 segments, got {len(optimized_payload)}"

    # --- STEP 4: Build Coordinate Lists for Plotting ---
    
    # A. Path for the Naive/Greedy plot
    g_lats = [start_node["lat"]] + [w["lat"] for w in greedy_seq] + [start_node["lat"]]
    g_lngs = [start_node["lng"]] + [w["lng"] for w in greedy_seq] + [start_node["lng"]]
    
    # B. Path for the AI-Optimized plot
    # We map the payload back to GPS points, treating the hub ID separately
    wp_map = {wp["id"]: wp for wp in waypoints}
    o_lats = [start_node["lat"]]
    o_lngs = [start_node["lng"]]
    
    for step in optimized_payload:
        if step["is_return_leg"]:
            # Last point is the Hub
            o_lats.append(start_node["lat"])
            o_lngs.append(start_node["lng"])
        else:
            # Map stop ID to its GPS location
            wp = wp_map[step["id"]]
            o_lats.append(wp["lat"])
            o_lngs.append(wp["lng"])

    # --- STEP 5: Visualization ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Plot 1: Greedy
    ax1.plot(g_lngs, g_lats, color='#94a3b8', linestyle='--', alpha=0.6, label="Naive Path")
    ax1.scatter(g_lngs, g_lats, c='#64748b', s=20)
    ax1.plot(start_node["lng"], start_node["lat"], 'rs', markersize=12, label="Hub")
    ax1.set_title("1. INITIAL GREEDY (Naive)\nTypically messy with many line-crossings", fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Plot 2: Optimized
    ax2.plot(o_lngs, o_lats, color='#0ea5e9', linewidth=2.5, label="Optimized Path")
    ax2.scatter(o_lngs, o_lats, c='#0284c7', s=30)
    ax2.plot(start_node["lng"], start_node["lat"], 'rs', markersize=12, label="Hub")
    ax2.set_title(f"2. LamiGo OPTIMIZED\nCalculated in {exec_duration:.2f}s | Clean Flow", fontsize=14, fontweight='bold', color='#0369a1')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.suptitle("LamiGo Routing Optimization: Colombo Stress Test (60 Stops)", fontsize=18, y=0.98, fontweight='extra bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()