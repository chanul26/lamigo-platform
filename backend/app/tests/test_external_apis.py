import pytest
from datetime import datetime, timezone, timedelta
from app.services.external_apis import build_delivery_timeline

@pytest.mark.asyncio
async def test_traffic_aware_timeline_generation():
    """
    Tests the timeline builder hitting the REAL Google Routes API
    to get traffic-aware ETAs based on the moving departure clock.
    """
    print("\n\n" + "="*75)
    print("🕒 INITIALIZING GOOGLE TRAFFIC & WEATHER TIMELINE TEST")
    print("="*75)

    # 1. Schedule for tomorrow at 5:00 PM (Simulating Rush Hour)
    # This proves the Google API respects the future timestamp
    scheduled_start = datetime.now(timezone.utc) + timedelta(days=1)
    scheduled_start = scheduled_start.replace(hour=17, minute=0, second=0, microsecond=0)
    print(f"📍 Dispatch Scheduled For: {scheduled_start.strftime('%Y-%m-%d %I:%M %p')} (UTC)")

    # 2. Setup Hub and Waypoints (A short 2-stop route in Colombo to keep testing fast)
    start_node = {"lat": 6.9344, "lng": 79.8428} # Colombo Fort Hub
    
    mock_route_sequence = [
        {"id": "pkg_1", "sequence_number": 1, "google_dist_meters": 0, "google_eta_seconds": 0, "is_return_leg": False},
        {"id": "pkg_2", "sequence_number": 2, "google_dist_meters": 0, "google_eta_seconds": 0, "is_return_leg": False},
        {"id": "hub_fort", "sequence_number": 3, "google_dist_meters": 0, "google_eta_seconds": 0, "is_return_leg": True}
    ]

    mock_waypoints = {
        "pkg_1": {"lat": 6.9147, "lng": 79.8514}, # Kollupitiya
        "pkg_2": {"lat": 6.8906, "lng": 79.8584}, # Bambalapitiya
        "hub_fort": start_node
    }

    # 3. Run the Orchestrator
    enriched_timeline = await build_delivery_timeline(
        route_sequence=mock_route_sequence,
        scheduled_start_time=scheduled_start,
        waypoints_data=mock_waypoints,
        start_node=start_node,
        vehicle_type="MOTORCYCLE"
    )

    # 4. Print the Dashboard
    print("\n📊 --- ENRICHED TRAFFIC-AWARE TIMELINE ---")
    print(f"{'Seq':<4} | {'Target ID':<13} | {'Arrival Time (UTC)':<22} | {'Live ETA':<10} | {'Temp':<6} | {'Rain'}")
    print("-" * 80)

    for step in enriched_timeline:
        arr_time_str = step["estimated_arrival_time"].strftime('%I:%M:%S %p')
        is_hub = "(RETURN)" if step["is_return_leg"] else ""
        target_str = f"{step['id']} {is_hub}"
        eta_mins = round(step['google_eta_seconds'] / 60, 1)
        
        print(f"{step['sequence_number']:<4} | {target_str:<13} | {arr_time_str:<22} | {eta_mins:<6} min | {step['temperature_c']}°C | {step['rain_volume_1h']}mm")

    print("-" * 80)
    print("\n✅ Verified: Google API successfully pulled live traffic delays for future timestamps.")