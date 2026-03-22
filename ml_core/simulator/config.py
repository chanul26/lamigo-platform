"""
config.py

This file serves as the "Single Source of Truth" for the LamiGo Logistics Digital Twin.
It contains the hardcoded physical boundaries, operational constraints, and demographic 
probabilities for generating realistic synthetic data across different Sri Lankan cities.
"""

# The exact order of location types expected by our probability arrays below.
# This must match the SQLAlchemy LocationType Enum exactly.
LOCATION_CHOICES = ['HOME', 'APARTMENT', 'OFFICE', 'WAREHOUSE', 'RETAIL_STORE', 'OTHER']

BRANCH_CONFIGURATIONS = {
    "B_001": {
        "facility_name": "Colombo Main Hub",
        
        # Geographic Anchors: The exact warehouse door (Latitude, Longitude)
        "origin_coordinates": {"latitude": 6.894766, "longitude": 79.8904568}, 
        
        # Spatial Boundaries: Custom GeoJSON Polygon (Format: [Longitude, Latitude])
        # Customers for B_001 will strictly spawn inside this shape.
        "service_area_polygon": [
            [79.9029717, 6.9094875],
            [79.8830572, 6.9219662],
            [79.8580582, 6.9218260],
            [79.8464767, 6.9173393],
            [79.8567871, 6.8790606],
            [79.9004294, 6.8804628],
            [79.9029717, 6.9094875] # Closes the loop
        ],
        
        # Fleet & Operational Constraints
        "allocated_fleet_size": 12,
        "shift_start_time": "08:00:00",
        
        # Hub Friction Metrics (In Seconds)
        # Colombo is a massive, busy hub, so handover takes longer.
        "mean_dispatch_friction_sec": 1800,       # 30 mins average sorting/loading time
        "dispatch_friction_std_dev": 300,         # 5 mins variance
        
        # Demographics: Urban Colombo 
        # High density of Apartments and Offices. High rate of 'OTHER' (unverified pins).
        # Maps to: ['HOME', 'APARTMENT', 'OFFICE', 'WAREHOUSE', 'RETAIL_STORE', 'OTHER']
        "location_type_probs": [0.35, 0.25, 0.15, 0.02, 0.03, 0.20]
    },
    
    "B_002": {
        "facility_name": "Galle Southern Hub",
        
        # Geographic Anchors: The exact warehouse door (Latitude, Longitude)
        "origin_coordinates": {"latitude": 6.0596201, "longitude": 80.203893},
        
        # Spatial Boundaries: Custom GeoJSON Polygon (Format: [Longitude, Latitude])
        # Customers for B_002 will strictly spawn inside this shape.
        "service_area_polygon": [
            [80.2272282, 6.0844424],
            [80.1933241, 6.0841883],
            [80.1805461, 6.0572510],
            [80.2181133, 6.0242976],
            [80.2417099, 6.0614865],
            [80.2272282, 6.0844424] # Closes the loop
        ],
        
        # Fleet & Operational Constraints
        "allocated_fleet_size": 8,
        "shift_start_time": "08:30:00",
        
        # Hub Friction Metrics (In Seconds)
        # Galle is a smaller, leaner hub, so handover is faster.
        "mean_dispatch_friction_sec": 900,        # 15 mins average sorting/loading time
        "dispatch_friction_std_dev": 180,         # 3 mins variance
        
        # Demographics: Suburban/Coastal Galle
        # Mostly standalone homes and villas. Very few high-rise apartments.
        # Maps to: ['HOME', 'APARTMENT', 'OFFICE', 'WAREHOUSE', 'RETAIL_STORE', 'OTHER']
        "location_type_probs": [0.60, 0.05, 0.05, 0.02, 0.03, 0.25]
    }
}

# Global Simulation Parameters
TOTAL_CUSTOMER_POPULATION = 640
TOTAL_DRIVER_POOL = 20