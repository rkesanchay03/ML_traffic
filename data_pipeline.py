import pandas as pd
import numpy as np
from datetime import datetime

# File paths
RAW_DATA_PATH = r"C:\Users\Sanchay\Desktop\Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv"
PROCESSED_DATA_PATH = r"C:\Users\Sanchay\OneDrive\Desktop\flipkart\dataset_processed.csv"

def clean_data(df):
    print("Initial shape:", df.shape)
    
    # 1. Fix nulls
    # zone: missing -> "unknown"
    if 'zone' in df.columns:
        df['zone'] = df['zone'].fillna("unknown")
    else:
        df['zone'] = "unknown"
        
    # junction: missing -> "unknown"
    if 'junction' in df.columns:
        df['junction'] = df['junction'].fillna("unknown")
    else:
        df['junction'] = "unknown"
        
    # 2. Parse time
    if 'start_datetime' in df.columns:
        df['start_datetime'] = pd.to_datetime(df['start_datetime'], format='ISO8601', utc=True)
        df['hour_of_day'] = df['start_datetime'].dt.hour
        df['day_of_week'] = df['start_datetime'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Target label: priority
    if 'priority' in df.columns:
        # Assuming Priority is 'High' / 'Low' or similar
        df['target'] = df['priority'].apply(lambda x: 1 if str(x).lower() == 'high' else 0)
        
    return df

def feature_engineering(df):
    # From event columns
    if 'event_cause' in df.columns:
        df['event_cause'] = df['event_cause'].fillna("unknown")
    if 'event_type' in df.columns:
        df['event_type'] = df['event_type'].apply(lambda x: 1 if str(x).lower() == 'planned' else 0)
    if 'requires_road_closure' in df.columns:
        df['requires_road_closure'] = df['requires_road_closure'].apply(lambda x: 1 if str(x).lower() in ['true', '1', 'yes'] else 0)
    if 'corridor' in df.columns:
        df['corridor'] = df['corridor'].fillna("unknown")
    if 'veh_type' in df.columns:
        df['veh_type'] = df['veh_type'].fillna("unknown")

    # Save processed dataframe
    # We only keep the features we need for modeling
    features = [
        'event_cause', 'event_type', 'requires_road_closure', 'corridor', 
        'veh_type', 'hour_of_day', 'day_of_week', 'is_weekend', 'zone', 'target'
    ]
    
    # Only keep available columns
    available_features = [col for col in features if col in df.columns]
    df_processed = df[available_features].copy()
    
    return df_processed

if __name__ == "__main__":
    print(f"Loading data from {RAW_DATA_PATH}")
    df = pd.read_csv(RAW_DATA_PATH)
    
    print("Cleaning data...")
    df_clean = clean_data(df)
    
    print("Engineering features...")
    df_processed = feature_engineering(df_clean)
    
    print(f"Processed shape: {df_processed.shape}")
    print(f"Saving to {PROCESSED_DATA_PATH}")
    df_processed.to_csv(PROCESSED_DATA_PATH, index=False)
    print("Done!")
