import os
import joblib
import torch
import torch.nn as nn
from typing import List, Dict, Any
from datetime import datetime

# ==============================================================================
# 1. ACTUAL LAMIGO DEEPFM ARCHITECTURE (From Phase 4 Notebook)
# ==============================================================================
class LamiGoDeepFM(nn.Module):
    def __init__(self, sparse_feature_dims, num_dense_features, embed_dim=8, dropout_rate=0.1):
        super(LamiGoDeepFM, self).__init__()

        self.sparse_features = list(sparse_feature_dims.keys())
        self.embed_dim = embed_dim
        self.dropout_rate = dropout_rate

        self.embeddings = nn.ModuleDict({
            feat: nn.Embedding(num_embeddings=vocab_size, embedding_dim=embed_dim)
            for feat, vocab_size in sparse_feature_dims.items()
        })

        self.fm_1st_order_embeddings = nn.ModuleDict({
            feat: nn.Embedding(num_embeddings=vocab_size, embedding_dim=1)
            for feat, vocab_size in sparse_feature_dims.items()
        })

        self.fm_1st_order_dense = nn.Linear(num_dense_features, 1)

        dnn_input_dim = (len(sparse_feature_dims) * embed_dim) + num_dense_features

        self.dnn = nn.Sequential(
            nn.Linear(dnn_input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),

            nn.Linear(64, 1)
        )

    def forward(self, x_sparse, x_dense):
        sparse_embeds = [
            self.embeddings[feat](x_sparse[:, i])
            for i, feat in enumerate(self.sparse_features)
        ]
        embed_tensor = torch.stack(sparse_embeds, dim=1)

        if self.training:
            mask = torch.empty(embed_tensor.shape[:2], device=embed_tensor.device).bernoulli_(1 - self.dropout_rate)
            mask = mask.unsqueeze(-1)
            embed_tensor = embed_tensor * mask

        fm_1st_sparse = torch.stack([
            self.fm_1st_order_embeddings[feat](x_sparse[:, i])
            for i, feat in enumerate(self.sparse_features)
        ], dim=1).sum(dim=1)

        fm_1st_dense = self.fm_1st_order_dense(x_dense)
        y_fm_1st = fm_1st_sparse + fm_1st_dense

        sum_of_square = torch.sum(embed_tensor, dim=1) ** 2
        square_of_sum = torch.sum(embed_tensor ** 2, dim=1)
        y_fm_2nd = 0.5 * torch.sum(sum_of_square - square_of_sum, dim=1, keepdim=True)

        embed_flat = embed_tensor.view(embed_tensor.size(0), -1)
        dnn_input = torch.cat([embed_flat, x_dense], dim=1)
        y_dnn = self.dnn(dnn_input)

        final_output = y_fm_1st + y_fm_2nd + y_dnn
        return final_output.squeeze()

# ==============================================================================
# 2. Global Memory Management & Feature Ordering
# ==============================================================================
_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_encoders = {}
_dense_scaler = None

# EXACT Order from Notebook
SPARSE_FEATURE_NAMES = [
    'driver_id', 'prev_customer_id', 'customer_id', 'destination_grid_id',
    'origin_grid_id', 'vehicle_type_id', 'location_type', 'prev_location_type',
    'is_pin_verified', 'weather_code', 'month_of_year', 'day_of_week',
    'hour_of_day', 'prev_cod_friction_code', 'trip_sequence_id', 'trip_progress_id'
]

def load_ml_artifacts():
    global _model, _encoders, _dense_scaler
    if _model is not None: return 
        
    print("🧠 Loading LamiGo ML Artifacts into Memory...")
    base_dir = os.path.join(os.path.dirname(__file__), "../ml_artifacts")
    meta_dir = os.path.join(base_dir, "metadata")
    
    # 1. Load Dense Scaler
    scaler_path = os.path.join(meta_dir, "dense_scaler.joblib")
    _dense_scaler = joblib.load(scaler_path)

    # 2. Load Label Encoders using exact notebook keys
    sparse_dims = {} 
    for feat_name in SPARSE_FEATURE_NAMES:
        le_path = os.path.join(meta_dir, f"le_{feat_name}.joblib")
        if os.path.exists(le_path):
            le = joblib.load(le_path)
            _encoders[feat_name] = le
            # NO + 1 HERE! Matches the notebook exactly
            sparse_dims[feat_name] = len(le.classes_)
        else:
            raise FileNotFoundError(f"Missing encoder: {le_path}")

    # 3. Initialize PyTorch Model
    # Exactly 6 features based on your notebook
    _model = LamiGoDeepFM(sparse_feature_dims=sparse_dims, num_dense_features=6)
    
    weights_path = os.path.join(base_dir, "lamigo_deepfm_weights.pth")
    _model.load_state_dict(torch.load(weights_path, map_location=_device))
    print("✅ DeepFM Weights loaded successfully.")
    
    _model.to(_device)
    _model.eval()

def safe_encode(feature_name: str, value: Any) -> int:
    """
    Safely transforms labels. If a value was never seen in training,
    it falls back to index 0 to prevent crashes.
    """
    encoder = _encoders.get(feature_name)
    if not encoder: return 0
    try:
        return encoder.transform([value])[0]
    except ValueError:
        return 0 # Fallback index for unseen values

# ==============================================================================
# 3. The Inference Orchestrator
# ==============================================================================
async def predict_trip_etas(enriched_timeline: List[Dict], db_context_map: Dict, vehicle_type: str, driver_id: str) -> List[Dict]:
    load_ml_artifacts()
    
    sparse_batch = {feat: [] for feat in SPARSE_FEATURE_NAMES}
    dense_batch = []
    
    # Lag trackers
    prev_loc_type = "WAREHOUSE" 
    prev_cust_id = "HUB"
    prev_cod_code = "NO_COD" 
    prev_cod_amt = 0.0
    
    total_stops = max(1, len(enriched_timeline))

    for step in enriched_timeline:
        task_id = step["id"]
        arr_time: datetime = step["estimated_arrival_time"]
        
        if step.get("is_return_leg", False):
            db_data = {"location_type": "WAREHOUSE", "weight_kg": 0.0, "customer_id": "HUB", "is_cod": False, "cod_amount": 0.0}
        else:
            db_data = db_context_map.get(task_id, {"location_type": "HOME", "customer_id": "UNKNOWN", "is_cod": False, "cod_amount": 0.0})

        # 1. Sparse Vector Map
        sparse_batch["driver_id"].append(safe_encode("driver_id", driver_id))
        sparse_batch["prev_customer_id"].append(safe_encode("prev_customer_id", prev_cust_id))
        sparse_batch["customer_id"].append(safe_encode("customer_id", db_data.get("customer_id")))
        sparse_batch["destination_grid_id"].append(safe_encode("destination_grid_id", step.get("destination_grid", "UNKNOWN")))
        sparse_batch["origin_grid_id"].append(safe_encode("origin_grid_id", step.get("origin_grid", "UNKNOWN")))
        sparse_batch["vehicle_type_id"].append(safe_encode("vehicle_type_id", vehicle_type))
        sparse_batch["location_type"].append(safe_encode("location_type", db_data["location_type"]))
        sparse_batch["prev_location_type"].append(safe_encode("prev_location_type", prev_loc_type))
        sparse_batch["is_pin_verified"].append(safe_encode("is_pin_verified", db_data.get("is_pin_verified", False)))
        sparse_batch["weather_code"].append(safe_encode("weather_code", step["weather_code"]))
        sparse_batch["month_of_year"].append(safe_encode("month_of_year", arr_time.month))
        sparse_batch["day_of_week"].append(safe_encode("day_of_week", arr_time.weekday()))
        sparse_batch["hour_of_day"].append(safe_encode("hour_of_day", arr_time.hour))
        sparse_batch["prev_cod_friction_code"].append(safe_encode("prev_cod_friction_code", prev_cod_code))
        sparse_batch["trip_sequence_id"].append(safe_encode("trip_sequence_id", step["sequence_number"]))
        sparse_batch["trip_progress_id"].append(safe_encode("trip_progress_id", round(step["sequence_number"] / total_stops, 2)))
        
        # 2. Dense Vector (Strictly 6 features as per Notebook)
        raw_dense = [[
            float(step["google_eta_seconds"]),
            float(step["google_dist_meters"]),
            float(prev_cod_amt),
            float(step["rain_volume_1h"]),
            float(step["sequence_number"]),
            float(step["sequence_number"] / total_stops)
        ]]
        scaled_dense = _dense_scaler.transform(raw_dense)[0]
        dense_batch.append(scaled_dense.tolist())
        
        # 3. Update Lags
        prev_loc_type = db_data["location_type"]
        prev_cust_id = db_data.get("customer_id", "UNKNOWN")
        prev_cod_code = "COD_PENDING" if db_data.get("is_cod") else "NO_COD"
        prev_cod_amt = float(db_data.get("cod_amount", 0.0))

    # -------------------------------------------------------------------------
    # PyTorch Batch Forward Pass
    # -------------------------------------------------------------------------
    # Convert dictionary of arrays to dictionary of tensors to match `self.embeddings[feat](x_sparse[:, i])`
    # We must convert the dictionary into a 2D tensor in the exact order of SPARSE_FEATURE_NAMES
    sparse_tensor_list = [sparse_batch[feat] for feat in SPARSE_FEATURE_NAMES]
    # Transpose list of lists to match shape: (Batch, Num_Features)
    sparse_tensor_list = list(map(list, zip(*sparse_tensor_list))) 
    
    sparse_tensor = torch.tensor(sparse_tensor_list, dtype=torch.long).to(_device)
    dense_tensor = torch.tensor(dense_batch, dtype=torch.float32).to(_device)
    
    with torch.no_grad():
        predictions_scaled = _model(sparse_tensor, dense_tensor)
        
        if predictions_scaled.dim() == 0:
            predicted_etas_numpy = [predictions_scaled.item()]
        else:
            predicted_etas_numpy = predictions_scaled.cpu().numpy().flatten().tolist()

    # -------------------------------------------------------------------------
    # Payload Enrichment
    # -------------------------------------------------------------------------
    for i, step in enumerate(enriched_timeline):
        google_eta = step["google_eta_seconds"]
        ai_eta_seconds = int(predicted_etas_numpy[i])
        
        # Prevent impossible physics
        ai_eta_seconds = max(ai_eta_seconds, google_eta) 
        
        step["deepfm_eta_seconds"] = ai_eta_seconds
        step["friction_factor"] = round(ai_eta_seconds / google_eta, 2) if google_eta > 0 else 1.0

    return enriched_timeline