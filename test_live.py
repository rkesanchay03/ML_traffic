import requests

def test(label, payload):
    r = requests.post('http://127.0.0.1:8000/predict', json=payload)
    d = r.json()
    print(f"\n=== {label} ===")
    print(f"  Severity   : {d['severity']}  (P(High)={d['prob_high']}%, P(Low)={d['prob_low']}%)")
    print(f"  Confidence : {d['confidence']}%")
    print(f"  Officers   : {d['manpower']['officers']}")
    print(f"  Barricades : {d['manpower']['barricades']}")
    print(f"  Basis      : {d['manpower']['basis']}")
    print(f"  Diversions : {d['diversions']['count']}  Avg duration: {d['diversions']['avg_duration_min']} min")
    print("  Rationale:")
    for item in d['rationale']:
        print(f"    - {item}")
    print("  Feature Importances:")
    for imp in d['importances']:
        print(f"    {imp['feature']}: {imp['value']}%")

test("vehicle_breakdown, road closure, peak hour 19, North Zone", {
    "event_cause": "vehicle_breakdown", "event_type": 0, "requires_road_closure": 1,
    "veh_type": "heavy_vehicle", "hour_of_day": 19, "day_of_week": 1,
    "is_weekend": 0, "month": 3, "zone": "North Zone 2", "corridor": "Tumkur Road"
})

test("procession, no road closure, off-peak hour 14, Central Zone", {
    "event_cause": "procession", "event_type": 1, "requires_road_closure": 0,
    "veh_type": "unknown", "hour_of_day": 14, "day_of_week": 3,
    "is_weekend": 0, "month": 6, "zone": "Central Zone 1", "corridor": "Non-corridor"
})

test("water_logging, weekend, South Zone, Hosur Road", {
    "event_cause": "water_logging", "event_type": 0, "requires_road_closure": 1,
    "veh_type": "car", "hour_of_day": 5, "day_of_week": 6,
    "is_weekend": 1, "month": 7, "zone": "South Zone 2", "corridor": "Hosur Road"
})

test("tree_fall, planned, weekend morning, East Zone", {
    "event_cause": "tree_fall", "event_type": 1, "requires_road_closure": 0,
    "veh_type": "unknown", "hour_of_day": 9, "day_of_week": 5,
    "is_weekend": 1, "month": 5, "zone": "East Zone 1", "corridor": "Non-corridor"
})
