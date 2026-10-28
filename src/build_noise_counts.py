
import pandas as pd

from pathlib import Path

# Paths resolve relative to this file, so the project runs from any checkout.
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"


def load_and_preprocess_noise_data(file_path):
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for noise-related complaints
    noise_complaint_types = [
        'Noise - Residential',
        'Noise - Street/Sidewalk',
        'Noise - Commercial',
        'Noise - Vehicle',
        'Noise - House of Worship',
        'Noise - Park',
        'Noise - Helicopter',
        'Noise - Aircraft',
        'Noise - Train',
        'Noise - Ferry',
        'Noise - Other'
    ]
    df_noise = df[df['Complaint Type'].isin(noise_complaint_types)].copy()
    
    # Convert 'Created Date' to datetime objects
    df_noise['Created Date'] = pd.to_datetime(df_noise['Created Date'], errors='coerce')
    
    # Drop rows where 'Created Date' is NaT (Not a Time) after coercion
    df_noise.dropna(subset=['Created Date'], inplace=True)

    # Handle missing values in 'Incident Zip' and 'Latitude', 'Longitude'
    # For simplicity, we'll drop rows with missing zip codes or coordinates for now.
    # A more sophisticated approach might involve imputation or geocoding.
    df_noise.dropna(subset=['Incident Zip', 'Latitude', 'Longitude'], inplace=True)
    
    # Convert 'Incident Zip' to string to handle potential leading zeros or non-numeric zips
    df_noise['Incident Zip'] = df_noise['Incident Zip'].astype(str).str.split('.').str[0]

    # Aggregate noise complaints by zip code and month
    df_noise['YearMonth'] = df_noise['Created Date'].dt.to_period('M')
    noise_counts = df_noise.groupby(['Incident Zip', 'YearMonth']).size().reset_index(name='noise_complaint_count')
    
    # Convert YearMonth back to datetime for easier merging later
    noise_counts['YearMonth'] = noise_counts['YearMonth'].dt.to_timestamp()

    return noise_counts

if __name__ == '__main__':
    file_path = DATA_DIR / "311_complaint_level.csv"
    processed_noise_data = load_and_preprocess_noise_data(file_path)
    print(processed_noise_data.head())
    print(f"Processed noise data shape: {processed_noise_data.shape}")
    processed_noise_data.to_csv(DATA_DIR / "processed_noise_data.csv", index=False)
    print(f"Processed noise data saved to {DATA_DIR / 'processed_noise_data.csv'}")


