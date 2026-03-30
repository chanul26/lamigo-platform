import pytest
from datetime import datetime, timezone, timedelta
from app.services.ml_service import predict_trip_etas

@pytest.mark.asyncio
async def test_production_deepfm_batch_inference():
    """
    Tests the End-to-End PyTorch batch inference pipeline using the ACTUAL 
    .joblib scalers/encoders and .pth weights from the metadata folder.
    """
    print("\n\n" + "="*85)
    print("🧠 LamiGo DeepFM Production Weights & Artifacts Integration Test")
    print("="*85)

    # 1. Define a scheduled start time
    arr_time_1 = datetime.now(timezone.utc)
    arr_time_2 = arr_time_1 + timedelta(minutes=15)
    arr_time_3 = arr_time_2 + timedelta(minutes=20)

    # 2. Mock Timeline Payload 
    # (Mimicking external_apis.py output, plus the H3 grid hashes we need to add later in routing)
    mock_timeline = [
        {
            "id": "pkg_1", "sequence_number": 1, "is_return_leg": False, 
            "google_dist_meters": 4500, "google_eta_seconds": 900, 
            "weather_code": 501, "rain_volume_1h": 15.0, 
            "estimated_arrival_time": arr_time_1,
            "origin_grid": "893cbaaaaaaaaab", "destination_grid": "893cbaaaaaaaaac"
        },
        {
            "id": "pkg_2", "sequence_number": 2, "is_return_leg": False, 
            "google_dist_meters": 2000, "google_eta_seconds": 400, 
            "weather_code": 800, "rain_volume_1h": 0.0, 
            "estimated_arrival_time": arr_time_2,
            "origin_grid": "893cbaaaaaaaaac", "destination_grid": "893cbaaaaaaaaad"
        },
        {
            "id": "hub_galle", "sequence_number": 3, "is_return_leg": True, 
            "google_dist_meters": 5500, "google_eta_seconds": 1100, 
            "weather_code": 800, "rain_volume_1h": 0.0, 
            "estimated_arrival_time": arr_time_3,
            "origin_grid": "893cbaaaaaaaaad", "destination_grid": "893cbaaaaaaaaab"
        }
    ]

    # 3. Mock Database Context 
    # (Simulates fetching from Recipient and Package tables)
    db_context_map = {
        "pkg_1": {
            "customer_id": "CUST_991", "location_type": "APARTMENT", 
            "weight_kg": 5.0, "is_cod": True, "is_pin_verified": False
        },
        "pkg_2": {
            "customer_id": "CUST_002", "location_type": "HOME", 
            "weight_kg": 0.5, "is_cod": False, "is_pin_verified": True
        }
    }

    # 4. Execute the ML Service
    print("🚀 Loading artifacts, transforming data, and executing PyTorch Forward Pass...")
    start_time = datetime.now()
    
    final_payload = await predict_trip_etas(
        enriched_timeline=mock_timeline,
        db_context_map=db_context_map,
        vehicle_type="MOTORCYCLE",
        driver_id="DRV_007"
    )
    
    execution_time = (datetime.now() - start_time).total_seconds()

    # 5. Output Verification
    assert len(final_payload) == 3
    assert "deepfm_eta_seconds" in final_payload[0]

    print(f"\n✅ Tensor Matrix compiled and processed in {execution_time:.4f} seconds!")
    print(f"\n{'Seq':<4} | {'Target ID':<10} | {'Location':<10} | {'Google ETA':<12} | {'DeepFM ETA':<12} | {'Friction'}")
    print("-" * 85)

    for step in final_payload:
        loc_type = "WAREHOUSE" if step["is_return_leg"] else db_context_map[step['id']]["location_type"]
        
        g_eta = round(step["google_eta_seconds"] / 60, 1)
        ai_eta = round(step["deepfm_eta_seconds"] / 60, 1)
        
        friction_str = f"{step['friction_factor']}x"
        if step['friction_factor'] > 1.2:
            friction_str = f"⚠️ {friction_str}"

        print(f"{step['sequence_number']:<4} | {step['id']:<10} | {loc_type:<10} | {g_eta:<7} min | {ai_eta:<7} min | {friction_str}")

    print("-" * 85)