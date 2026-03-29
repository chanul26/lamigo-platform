import pytest
import time
import matplotlib.pyplot as plt
from typing import List, Dict

# Import the core engine we just built
from app.services.routing_service import optimize_trip_sequence

@pytest.mark.asyncio
async def test_lamigo_routing_engine_15_stops():
    """
    Tests the Haversine + Simulated Annealing + Google Circuity Penalty engine
    using 15 realistic delivery coordinates in the Southern Province of Sri Lanka.
    """
    print("\n\n" + "="*50)
    print("🚀 INITIALIZING LAMIGO ROUTING ENGINE TEST")
    print("="*50)

    # 1. Define the Hub (Start and End Node)
    # Using the Galle Main Hub (Approximate coordinates near Galle Fort)
    start_node = {"id": "hub_galle_start", "lat": 6.0258, "lng": 80.2176}
    end_node = {"id": "hub_galle_end", "lat": 6.0258, "lng": 80.2176}

    # 2. Define 15 Realistic Sri Lankan Waypoints (Coastal & Inland)
    waypoints: List[Dict[str, float | str]] = [
        {"id": "pkg_1_unawatuna", "lat": 6.0118, "lng": 80.2483},
        {"id": "pkg_2_karapitiya", "lat": 6.0645, "lng": 80.2222},
        {"id": "pkg_3_hikkaduwa", "lat": 6.1396, "lng": 80.1014},
        {"id": "pkg_4_ambalangoda", "lat": 6.2345, "lng": 80.0543},
        {"id": "pkg_5_weligama", "lat": 5.9736, "lng": 80.4283},
        {"id": "pkg_6_mirissa", "lat": 5.9483, "lng": 80.4566},
        {"id": "pkg_7_matara", "lat": 5.9496, "lng": 80.5353},
        {"id": "pkg_8_koggala", "lat": 5.9961, "lng": 80.3275},
        {"id": "pkg_9_talpe", "lat": 6.0028, "lng": 80.2831},
        {"id": "pkg_10_ahangama", "lat": 5.9694, "lng": 80.3667},
        {"id": "pkg_11_baddegama", "lat": 6.1772, "lng": 80.1989},
        {"id": "pkg_12_elpitiya", "lat": 6.2736, "lng": 80.1603},
        {"id": "pkg_13_akmeemana", "lat": 6.0792, "lng": 80.2525},
        {"id": "pkg_14_habaraduwa", "lat": 5.9922, "lng": 80.3069},
        {"id": "pkg_15_dodanduwa", "lat": 6.1011, "lng": 80.1417},
    ]

    # Start the clock to measure algorithm efficiency
    start_time = time.time()

    # 3. Execute the Master Orchestrator (Simulating a Motorcycle Dispatch)
    optimized_sequence = await optimize_trip_sequence(
        start_node=start_node,
        end_node=end_node,
        waypoints=waypoints,
        vehicle_type="MOTORCYCLE"
    )

    execution_time = time.time() - start_time

    # 4. Assertions (To ensure the engine didn't drop or duplicate any packages)
    assert len(optimized_sequence) == 15, f"Expected 15 tasks, got {len(optimized_sequence)}"
    
    # ==========================================
    # 5. Output the Results to Terminal
    # ==========================================
    print(f"\n✅ ROUTING COMPLETE in {execution_time:.3f} seconds!")
    
    # Table Header (Now explicitly includes the Source column)
    print(f"{'Seq':<5} | {'Package ID':<20} | {'Dist (m)':<10} | {'ETA (s)':<10} | {'Source':<10}")
    print("-" * 75)
    
    total_distance = 0
    total_time = 0

    # Print every step in the perfectly ordered sequence
    for step in optimized_sequence:
        print(f"{step['sequence_number']:<5} | {step['id']:<20} | {step['google_dist_meters']:<10} | {step['google_eta_seconds']:<10} | {step.get('data_source', 'UNKNOWN'):<10}")
        total_distance += step['google_dist_meters']
        total_time += step['google_eta_seconds']

    print("-" * 75)
    print(f"Total Google Predicted Distance: {total_distance / 1000:.2f} km")
    print(f"Total Google Predicted Driving Time: {total_time / 60:.2f} minutes\n")

    # ==========================================
    # 6. VISUALIZE THE ROUTE (Matplotlib)
    # ==========================================
    
    # Build the ordered list of coordinates
    # Step A: Start at the Hub
    route_lats = [start_node["lat"]]
    route_lngs = [start_node["lng"]]
    labels = ["HUB (Galle)"]

    # Step B: Add the optimized waypoints in order based on the final sequence
    waypoint_dict = {wp["id"]: wp for wp in waypoints}
    for step in optimized_sequence:
        wp = waypoint_dict[step["id"]]
        route_lats.append(wp["lat"])
        route_lngs.append(wp["lng"])
        
        # Clean up the label for the graph (e.g., "pkg_1_unawatuna" -> "Unawatuna")
        clean_name = step["id"].split("_")[-1].capitalize()
        labels.append(clean_name)

    # Step C: Return to the Hub at the end
    route_lats.append(end_node["lat"])
    route_lngs.append(end_node["lng"])
    labels.append("HUB (Return)")

    # --- Plotting Logic ---
    plt.figure(figsize=(10, 8))
    
    # Draw the lines connecting the points to simulate the physical journey
    plt.plot(route_lngs, route_lats, marker='o', linestyle='-', color='#2563eb', linewidth=2, markersize=8)
    
    # Highlight the Hub in a distinct Red square
    plt.plot(start_node["lng"], start_node["lat"], marker='s', color='#ef4444', markersize=12, label="Galle Hub")

    # Add text labels to each point
    for i, txt in enumerate(labels):
        # Only label the first instance of the Hub to avoid text overlap
        if i == len(labels) - 1: continue 
        plt.annotate(txt, (route_lngs[i], route_lats[i]), textcoords="offset points", xytext=(5,5), ha='left', fontsize=9)

    plt.title(f"LamiGo Optimized Route: 15 Stops in Southern Province\nDistance: {total_distance/1000:.2f} km | Time: {total_time/60:.2f} min", fontweight='bold')
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    # Pop open the visualizer window!
    plt.show()