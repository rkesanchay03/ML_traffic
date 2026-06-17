"""
Comprehensive data pipeline + model training that:
1. Fixes data leakage (removes corridor as direct predictor since it == priority)
2. Trains XGBoost on meaningful features: event_cause, requires_road_closure, hour_of_day,
   day_of_week, is_weekend, veh_type, event_type, zone
3. Builds data-driven lookup tables from the dataset for:
   - Manpower (officers + barricades) based on historical High-priority patterns per cause
   - Duration stats per cause + priority
   - Feature importances at grouped level (not OHE-expanded)
   - Rationale facts derived from actual data
4. Saves model.pkl and stats.json for the backend
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

RAW_DATA = r"C:\Users\Sanchay\Desktop\Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv"
PROCESSED_DATA = r"C:\Users\Sanchay\OneDrive\Desktop\flipkart\dataset_processed.csv"
MODEL_PATH = r"C:\Users\Sanchay\OneDrive\Desktop\flipkart\model.pkl"
STATS_PATH = r"C:\Users\Sanchay\OneDrive\Desktop\flipkart\stats.json"

print("=" * 60)
print("STEP 1: Loading & Cleaning Data")
print("=" * 60)

df = pd.read_csv(RAW_DATA)
print(f"Raw data shape: {df.shape}")

# Parse datetimes
df['start_datetime']    = pd.to_datetime(df['start_datetime'],    format='ISO8601', utc=True, errors='coerce')
df['closed_datetime']   = pd.to_datetime(df['closed_datetime'],   format='ISO8601', utc=True, errors='coerce')
df['resolved_datetime'] = pd.to_datetime(df['resolved_datetime'], format='ISO8601', utc=True, errors='coerce')

# Duration in minutes
df['end_time']      = df['closed_datetime'].fillna(df['resolved_datetime'])
df['duration_min']  = (df['end_time'] - df['start_datetime']).dt.total_seconds() / 60
df['duration_min']  = df['duration_min'].clip(lower=0)

# Temporal features
df['hour_of_day']   = df['start_datetime'].dt.hour.fillna(12).astype(int)
df['day_of_week']   = df['start_datetime'].dt.dayofweek.fillna(0).astype(int)
df['is_weekend']    = (df['day_of_week'] >= 5).astype(int)
df['month']         = df['start_datetime'].dt.month.fillna(1).astype(int)

# Clean categoricals
df['event_cause']   = df['event_cause'].fillna('unknown').str.lower().str.strip().str.replace(' ', '_')
df['event_type']    = df['event_type'].apply(lambda x: 1 if str(x).lower() == 'planned' else 0)
df['requires_road_closure'] = df['requires_road_closure'].apply(
    lambda x: 1 if str(x).lower() in ['true','1','yes'] else 0
)
df['veh_type']      = df['veh_type'].fillna('unknown').str.lower().str.strip().str.replace(' ', '_')
df['zone']          = df['zone'].fillna('unknown').str.strip()
df['corridor']      = df['corridor'].fillna('Non-corridor').str.strip()

# *** KEY FIX: The target label ***
# In this dataset, priority=High if and only if corridor != 'Non-corridor'.
# So we MUST NOT use 'corridor' as a feature — it is equivalent to the target.
# We also remove 'junction' which is too sparse.
# We train on the meaningful signal features only.

df['target'] = df['priority'].apply(lambda x: 1 if str(x).lower() == 'high' else 0)

print(f"Target distribution:\n{df['target'].value_counts()}")
print()

# -------------------------------------------------------
# STEP 2: Feature Engineering
# -------------------------------------------------------
print("=" * 60)
print("STEP 2: Feature Engineering")
print("=" * 60)

# Hour buckets for better generalisation
def hour_bucket(h):
    if 0 <= h < 6:   return 'night'
    elif 6 <= h < 10: return 'morning_peak'
    elif 10 <= h < 16: return 'daytime'
    elif 16 <= h < 21: return 'evening_peak'
    else:              return 'late_night'

df['hour_bucket'] = df['hour_of_day'].apply(hour_bucket)

# High-risk cause flag (from data: vehicle_breakdown, construction, water_logging dominate High)
high_risk_causes = {'vehicle_breakdown', 'construction', 'water_logging', 'congestion', 'accident'}
df['is_high_risk_cause'] = df['event_cause'].apply(lambda x: 1 if x in high_risk_causes else 0)

FEATURES = [
    'event_cause',      # categorical
    'veh_type',         # categorical
    'zone',             # categorical
    'hour_bucket',      # categorical (derived)
    'event_type',       # binary: planned=1 / unplanned=0
    'requires_road_closure',  # binary
    'is_high_risk_cause',     # binary (derived)
    'day_of_week',      # numeric
    'is_weekend',       # binary
    'month',            # numeric
]

CAT_FEATURES = ['event_cause', 'veh_type', 'zone', 'hour_bucket']
NUM_FEATURES = ['event_type', 'requires_road_closure', 'is_high_risk_cause',
                'day_of_week', 'is_weekend', 'month']

df_model = df[FEATURES + ['target']].dropna().copy()
print(f"Model dataframe shape: {df_model.shape}")
print(f"Features: {FEATURES}")
print()

X = df_model[FEATURES]
y = df_model['target']

# -------------------------------------------------------
# STEP 3: Model Training
# -------------------------------------------------------
print("=" * 60)
print("STEP 3: Training XGBoost Model")
print("=" * 60)

# Use OrdinalEncoder so XGBoost can understand categories
preprocessor = ColumnTransformer(transformers=[
    ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), CAT_FEATURES)
], remainder='passthrough')

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=y.value_counts()[0] / y.value_counts()[1],  # handle class imbalance
        eval_metric='logloss',
        random_state=42,
        n_jobs=-1
    ))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model.fit(X_train, y_train)

y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:,1]

acc = accuracy_score(y_test, y_pred)
f1  = f1_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f}")
print(f"F1 Score: {f1:.4f}")
print()
print(classification_report(y_test, y_pred, target_names=['Low','High']))

# Cross-validation
cv_scores = cross_val_score(model, X, y, cv=5, scoring='f1')
print(f"5-Fold CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print()

# -------------------------------------------------------
# STEP 4: Grouped Feature Importance (meaningful)
# -------------------------------------------------------
print("=" * 60)
print("STEP 4: Computing Feature Importances")
print("=" * 60)

classifier_   = model.named_steps['classifier']
raw_imp       = classifier_.feature_importances_

# Map raw importances back to original feature groups
# OrdinalEncoder gives one column per categorical feature
# remainder='passthrough' keeps numeric features in order
n_cat = len(CAT_FEATURES)
n_num = len(NUM_FEATURES)

cat_importances = {feat: raw_imp[i]             for i, feat in enumerate(CAT_FEATURES)}
num_importances = {feat: raw_imp[n_cat + i]     for i, feat in enumerate(NUM_FEATURES)}

all_importances = {**cat_importances, **num_importances}
total = sum(all_importances.values())
feat_imp_pct = {k: round(float(v) / float(total) * 100, 1) for k, v in sorted(all_importances.items(), key=lambda x: -float(x[1]))}
print("Feature importances (grouped):")
for f, v in feat_imp_pct.items():
    print(f"  {f}: {v}%")

# -------------------------------------------------------
# STEP 5: Build Data-Driven Stats from Dataset
# -------------------------------------------------------
print()
print("=" * 60)
print("STEP 5: Building Data-Driven Stats from Dataset")
print("=" * 60)

# 5a. Officers & Barricades from historical data
# The dataset shows that High priority events require deployment.
# We model officers as proportional to historical HIGH event count per cause per corridor
# Barricades scale with requires_road_closure rate

# Historical High % per event_cause
cause_high_rate = df.groupby('event_cause')['target'].agg(['sum','count'])
cause_high_rate['high_pct'] = (cause_high_rate['sum'] / cause_high_rate['count'] * 100).round(1)
cause_high_rate = cause_high_rate.to_dict('index')

# Avg duration (minutes) per (priority, event_cause) - capped at 3 days
duration_by_cause_priority = df[df['duration_min'] < 4320].groupby(
    ['event_cause','target'])['duration_min'].mean().round(0).astype(int)
duration_dict = {}
for (cause, priority), dur in duration_by_cause_priority.items():
    if cause not in duration_dict:
        duration_dict[cause] = {}
    duration_dict[cause][str(priority)] = int(dur)

# Officer recommendation: derived from severity + cause
# Rule from data: High causes vehicle_breakdown, construction, water_logging, congestion
# Base officers for HIGH: scale from 10-30 based on historical high-priority rate of that cause
def calc_officers(event_cause, severity, requires_road_closure):
    base = 10 if severity == 'HIGH' else 3
    cause_data = cause_high_rate.get(event_cause, {})
    high_pct = cause_data.get('high_pct', 50)
    # Scale: high_pct 100% → 30 officers, 50% → 15
    officers = int(base + (high_pct / 100) * 20) if severity == 'HIGH' else base
    if requires_road_closure:
        officers = int(officers * 1.4)
    return min(officers, 50)

def calc_barricades(severity, requires_road_closure):
    if severity == 'HIGH':
        return 20 if requires_road_closure else 10
    else:
        return 5 if requires_road_closure else 2

# Road closure rate per cause (from data)
closure_by_cause = df.groupby('event_cause')['requires_road_closure'].mean().round(3).to_dict()

# Top risky corridors (from data - corridors that only appear with High priority)
risky_corridors = [c for c in df[df['target']==1]['corridor'].value_counts().head(5).index.tolist()
                   if c != 'Non-corridor']

# Peak hours from data (hours with highest proportion of High events)
hour_priority = df.groupby('hour_of_day')['target'].mean()
peak_hours    = hour_priority[hour_priority > hour_priority.median()].index.tolist()

# Top causes by High event count
top_high_causes = df[df['target']==1]['event_cause'].value_counts().head(5).index.tolist()

# Zone stats
zone_high_rate = df.groupby('zone')['target'].mean().sort_values(ascending=False).round(3).to_dict()

print("Duration dict sample:", list(duration_dict.items())[:3])
print("Risky corridors:", risky_corridors)
print("Peak hours:", sorted(peak_hours))
print("Top High causes:", top_high_causes)
print()

# -------------------------------------------------------
# STEP 6: Save everything
# -------------------------------------------------------
print("=" * 60)
print("STEP 6: Saving model and stats")
print("=" * 60)

stats = {
    "feature_importances": {k: float(v) for k, v in feat_imp_pct.items()},
    "cause_high_rate": {k: {kk: float(vv) for kk, vv in v.items()} for k, v in cause_high_rate.items()},
    "duration_by_cause": {k: {sk: int(sv) for sk, sv in sv2.items()} for k, sv2 in duration_dict.items()},
    "closure_rate_by_cause": {k: float(v) for k, v in closure_by_cause.items()},
    "risky_corridors": [str(c) for c in risky_corridors],
    "peak_hours": [int(h) for h in sorted(peak_hours)],
    "top_high_causes": [str(c) for c in top_high_causes],
    "zone_high_rate": {k: float(v) for k, v in zone_high_rate.items()},
    "train_accuracy": round(float(acc), 4),
    "train_f1": round(float(f1), 4),
    "cat_features": CAT_FEATURES,
    "num_features": NUM_FEATURES,
    "all_features": FEATURES,
    # Corridor coordinate map for map plotting (actual Bengaluru coordinates)
    "corridor_coords": {
        "Mysore Road":       {"lat": 12.9460, "lon": 77.5300},
        "Bellary Road 1":    {"lat": 13.0437, "lon": 77.5970},
        "Bellary Road 2":    {"lat": 13.0200, "lon": 77.5900},
        "Tumkur Road":       {"lat": 13.0167, "lon": 77.5080},
        "Hosur Road":        {"lat": 12.8950, "lon": 77.6400},
        "ORR East 1":        {"lat": 12.9430, "lon": 77.6870},
        "ORR North 1":       {"lat": 13.0480, "lon": 77.6100},
        "Old Madras Road":   {"lat": 13.0020, "lon": 77.6550},
        "Magadi Road":       {"lat": 12.9600, "lon": 77.5050},
        "Bannerghata Road":  {"lat": 12.8700, "lon": 77.5960},
        "Hennur Main Road":  {"lat": 13.0630, "lon": 77.6380},
        "Kanakapura Road":   {"lat": 12.8960, "lon": 77.5500},
        "Non-corridor":      {"lat": 12.9716, "lon": 77.5946},
    }
}

joblib.dump(model, MODEL_PATH)
with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2, cls=NumpyEncoder)

print(f"Model saved to {MODEL_PATH}")
print(f"Stats saved to {STATS_PATH}")
print("Done!")
