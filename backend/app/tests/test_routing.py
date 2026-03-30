import pytest
import time
import matplotlib.pyplot as plt
from typing import List, Dict

# Import the core engine orchestrator
from app.services.routing_service import optimize_trip_sequence

@pytest.mark.asyncio
async def test_lamigo_routing_engine_15_stops():
    """
    Tests the 15-stop Southern Province route. 
    Now accounts for the +1 Return-to-Hub segment.
    """
    print("\n\n" + "="*50)
    print("🚀 INITIALIZING LAMIGO ROUTING ENGINE TEST")
    print("="*50)

    # 1. Setup Hub and Waypoints (Southern Coastal Route)
    start_node = {"id": "hub_galle_fort", "lat": 6.0258, "lng": 80.2176}
    end_node = {"id": "hub_galle_fort", "lat": 6.0258, "lng": 80.2176}

    waypoints = [
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

    start_time = time.time()

    # 2. Run Optimization
    optimized_sequence = await optimize_trip_sequence(
        start_node=start_node,
        end_node=end_node,
        waypoints=waypoints,
        vehicle_type="MOTORCYCLE"
    )

    execution_time = time.time() - start_time

    # Verify the payload contains 15 delivery tasks + 1 return leg = 16
    assert len(optimized_sequence) == 16, f"Expected 16 segments, got {len(optimized_sequence)}"
    
    # --- STEP 3: Output Results to Terminal ---
    print(f"\n✅ ROUTING COMPLETE in {execution_time:.3f} seconds!")
    print(f"{'Seq':<5} | {'Target ID':<20} | {'Dist (m)':<10} | {'ETA (s)':<10} | {'Source':<10}")
    print("-" * 75)
    
    total_distance = 0
    total_time = 0

    for step in optimized_sequence:
        # Check if this is the final return trip to label it clearly
        display_id = "RETURN TO HUB" if step["is_return_leg"] else step["id"]
        
        print(f"{step['sequence_number']:<5} | {display_id:<20} | {step['google_dist_meters']:<10} | {step['google_eta_seconds']:<10} | {step.get('data_source', 'UNKNOWN'):<10}")
        
        total_distance += step['google_dist_meters']
        total_time += step['google_eta_seconds']

    print("-" * 75)
    print(f"Total REAL-WORLD Distance: {total_distance / 1000:.2f} km")
    print(f"Total REAL-WORLD Driving Time: {total_time / 60:.2f} minutes\n")

    # --- STEP 4: Visualization ---
    route_lats = [start_node["lat"]]
    route_lngs = [start_node["lng"]]
    labels = ["HUB (Galle)"]

    waypoint_dict = {wp["id"]: wp for wp in waypoints}
    for step in optimized_sequence:
        if step["is_return_leg"]:
            route_lats.append(end_node["lat"])
            route_lngs.append(end_node["lng"])
            labels.append("RETURN TO HUB")
        else:
            wp = waypoint_dict[step["id"]]
            route_lats.append(wp["lat"])
            route_lngs.append(wp["lng"])
            labels.append(step["id"].split("_")[-1].capitalize())

    plt.figure(figsize=(10, 8))
    plt.plot(route_lngs, route_lats, marker='o', linestyle='-', color='#2563eb', linewidth=2)
    plt.plot(start_node["lng"], start_node["lat"], 'rs', markersize=12, label="Galle Hub")

    for i, txt in enumerate(labels):
        if i == len(labels) - 1 and txt == "RETURN TO HUB": continue # Don't double label the hub
        plt.annotate(txt, (route_lngs[i], route_lats[i]), textcoords="offset points", xytext=(5,5), ha='left', fontsize=9)

    plt.title(f"LamiGo 15-Stop Route (Southern Province)\nFull Trip: {total_distance/1000:.2f} km", fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.show()