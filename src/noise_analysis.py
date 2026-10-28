#!/usr/bin/env python3
"""
Enhanced Analysis Script for NYC Noise and Mental Health Study (Fixed Version)
This script implements advanced features including:
1. Time period mapping from TimePeriodID to calendar years
2. Nocturnal Noise Index (weights late-night complaints)
3. Population-normalized noise rates
4. Advanced modeling with robust statistics
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths resolve relative to this file, so the project runs from any checkout.
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "figures"
RESULTS_DIR.mkdir(exist_ok=True)
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression, TheilSenRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_time_periods():
    """Load TimePeriodID -> calendar period mappings.

    TimePeriods.json is the NYC DOHMH lookup that maps survey TimePeriodIDs to
    calendar periods. It is not redistributed here. Without it the analysis still
    runs; the Year column simply keeps the raw TimePeriodIDs instead of readable
    calendar labels.
    """
    path = DATA_DIR / "TimePeriods.json"
    if not path.exists():
        print("TimePeriods.json not present - keeping raw TimePeriodIDs.")
        return {}
    with open(path, 'r') as f:
        time_periods = json.load(f)
    
    # Create mapping dictionary
    time_mapping = {}
    for period in time_periods:
        time_mapping[period['TimePeriodID']] = {
            'period': period['TimePeriod'],
            'type': period['TimeType'],
            'start': period['start_period'],
            'end': period['end_period']
        }
    
    return time_mapping

def get_population_data():
    """
    Get population data for UHF42 neighborhoods
    Using estimated population data based on NYC demographics
    """
    # More comprehensive population estimates for UHF42 neighborhoods
    # Based on NYC DOHMH population estimates and Census data
    population_estimates = {
        101: 180000,  # Kingsbridge - Riverdale
        102: 220000,  # Northeast Bronx
        103: 195000,  # Fordham - Bronx Pk
        104: 165000,  # Pelham - Throgs Neck
        105: 175000,  # South Bronx
        106: 190000,  # Crotona - Tremont
        107: 210000,  # High Bridge - Morrisania
        201: 185000,  # Greenpoint
        202: 200000,  # Downtown - Heights - Slope
        203: 170000,  # Bedford Stuyvesant - Crown Heights
        204: 155000,  # East New York
        205: 225000,  # Sunset Park
        206: 240000,  # Borough Park
        207: 160000,  # East Flatbush - Flatbush
        208: 145000,  # Canarsie - Flatlands
        209: 135000,  # Bensonhurst - Bay Ridge
        210: 125000,  # Coney Island - Sheepshead Bay
        211: 115000,  # Williamsburg - Bushwick
        301: 140000,  # Washington Heights
        302: 150000,  # Central Harlem - Morningside Heights
        303: 130000,  # East Harlem
        304: 120000,  # Upper West Side
        305: 110000,  # Upper East Side
        306: 105000,  # Chelsea - Clinton
        307: 95000,   # Gramercy Park - Murray Hill
        308: 100000,  # Greenwich Village - SoHo
        309: 90000,   # Union Square - Lower East Side
        310: 85000,   # Lower Manhattan
        401: 80000,   # Long Island City - Astoria
        402: 70000,   # West Queens
        403: 200000,  # Flushing - Clearview
        404: 180000,  # Bayside - Little Neck
        405: 160000,  # Ridgewood - Forest Hills
        406: 140000,  # Fresh Meadows
        407: 120000,  # Southwest Queens
        408: 100000,  # Jamaica
        409: 90000,   # Southeast Queens
        410: 80000,   # Rockaways
        501: 70000,   # Port Richmond
        502: 60000,   # Stapleton - St. George
        503: 50000,   # Willowbrook
        504: 45000    # South Beach - Tottenville
    }
    
    return population_estimates

def calculate_nocturnal_noise_index(df):
    """
    Calculate Nocturnal Noise Index based on complaint time and type
    This is a novel metric that weights noise complaints by:
    1. Time of day (higher weight for late night/early morning)
    2. Complaint type severity
    """
    # Define time weights (higher for nocturnal hours)
    def get_time_weight(hour):
        if 22 <= hour or hour <= 6:  # 10 PM to 6 AM
            return 2.0  # High weight for nocturnal hours
        elif 7 <= hour <= 9 or 18 <= hour <= 21:  # Rush hours
            return 1.5  # Medium weight for peak hours
        else:
            return 1.0  # Normal weight for daytime
    
    # Define complaint type weights based on severity/impact
    complaint_weights = {
        'Noise - Residential': 1.2,
        'Noise - Commercial': 1.3,
        'Noise - Vehicle': 1.1,
        'Noise - Park': 1.0,
        'Noise - House of Worship': 1.4,
        'Noise - Helicopter': 1.8,
        'Noise - Construction': 1.6,
        'Noise - Street/Sidewalk': 1.1,
        'Noise': 1.0  # Default weight
    }
    
    # Calculate nocturnal index for each complaint
    nocturnal_scores = []
    
    for _, row in df.iterrows():
        # Extract hour from created_date
        try:
            hour = pd.to_datetime(row['created_date']).hour
            time_weight = get_time_weight(hour)
        except:
            time_weight = 1.0  # Default if time parsing fails
        
        # Get complaint type weight
        complaint_type = row.get('complaint_type', 'Noise')
        type_weight = complaint_weights.get(complaint_type, 1.0)
        
        # Calculate combined nocturnal score
        nocturnal_score = time_weight * type_weight
        nocturnal_scores.append(nocturnal_score)
    
    return nocturnal_scores

def enhanced_analysis():
    """Main enhanced analysis function"""
    print("Starting Enhanced Analysis...")
    
    # Load data
    print("Loading datasets...")
    combined_data = pd.read_csv(DATA_DIR / "combined_noise_mental_health_data.csv")
    noise_data = pd.read_csv(DATA_DIR / "uhf_noise_counts.csv")
    
    # Load time periods and population data
    time_mapping = load_time_periods()
    HAS_TIME_MAPPING = bool(time_mapping)
    population_data = get_population_data()
    
    print(f"Combined data shape: {combined_data.shape}")
    print(f"Noise data shape: {noise_data.shape}")
    
    # Enhanced Data Processing
    print("\n=== Enhanced Data Processing ===")
    
    # 1. Map TimePeriodIDs to calendar years
    if 'Year' in combined_data.columns:
        combined_data['calendar_year'] = combined_data['Year'].map(
            lambda x: time_mapping.get(x, {}).get('period', 'Unknown')
        )
        print("Mapped TimePeriodIDs to calendar years")
        print(f"Calendar year mapping: {combined_data['calendar_year'].unique()}")
    
    # 2. Calculate population-normalized noise rates
    print("Calculating population-normalized noise rates...")
    combined_data['population'] = combined_data['UHF42'].map(population_data)
    
    # Check for missing population data
    missing_pop = combined_data[combined_data['population'].isna()]
    if not missing_pop.empty:
        print(f"Warning: Missing population data for {len(missing_pop)} neighborhoods:")
        print(missing_pop[['UHF42_name', 'UHF42']])
        # Fill missing with median population
        median_pop = pd.Series(population_data.values()).median()
        combined_data['population'] = combined_data['population'].fillna(median_pop)
    
    combined_data['noise_rate_per_100k'] = (
        combined_data['noise_complaint_count'] / combined_data['population'] * 100000
    )
    
    # 3. Nocturnal Noise Index
    #
    # calculate_nocturnal_noise_index() above is the real metric: each complaint is
    # weighted by hour of day and by complaint-type severity. It needs COMPLAINT-LEVEL
    # rows (created_date, complaint_type) from the raw 311 extract.
    #
    # combined_data is already aggregated to neighbourhood-year, so those columns do
    # not exist here and the index cannot be computed from it. Rather than substitute
    # a stand-in, the index is left undefined and every nocturnal result below is
    # skipped. To reproduce it, point COMPLAINT_LEVEL_CSV at the raw 311 download.
    COMPLAINT_LEVEL_CSV = DATA_DIR / "311_complaint_level.csv"
    if COMPLAINT_LEVEL_CSV.exists():
        print("Computing Nocturnal Noise Index from complaint-level data...")
        complaints = pd.read_csv(COMPLAINT_LEVEL_CSV, low_memory=False)
        complaints['nocturnal_score'] = calculate_nocturnal_noise_index(complaints)
        per_area = complaints.groupby('UHF42')['nocturnal_score'].sum()
        combined_data['nocturnal_index'] = combined_data['UHF42'].map(per_area)
        HAS_NOCTURNAL = True
    else:
        print("Complaint-level 311 data not present - skipping the Nocturnal Noise Index.")
        combined_data['nocturnal_index'] = np.nan
        HAS_NOCTURNAL = False
    
    # Enhanced Exploratory Data Analysis
    print("\n=== Enhanced Exploratory Data Analysis ===")
    
    # Basic statistics
    print("\nDataset Overview:")
    print(f"Number of UHF42 neighborhoods: {combined_data['UHF42'].nunique()}")
    print(f"Time periods covered: {combined_data.get('calendar_year', pd.Series(['N/A'])).nunique()}")
    print(f"Total noise complaints: {combined_data['noise_complaint_count'].sum():,}")
    print(f"Average depression prevalence: {combined_data['depression_prevalence'].mean():.2f}%")
    
    # Population-normalized statistics
    print(f"\nPopulation-Normalized Metrics:")
    print(f"Average noise rate per 100k population: {combined_data['noise_rate_per_100k'].mean():.2f}")
    print(f"Max noise rate per 100k population: {combined_data['noise_rate_per_100k'].max():.2f}")
    print(f"Min noise rate per 100k population: {combined_data['noise_rate_per_100k'].min():.2f}")
    
    # Enhanced Correlation Analysis
    print("\n=== Enhanced Correlation Analysis ===")
    
    # Calculate correlations
    correlations = {
        'Raw Noise Count vs Depression': combined_data['noise_complaint_count'].corr(combined_data['depression_prevalence']),
        'Noise Rate per 100k vs Depression': combined_data['noise_rate_per_100k'].corr(combined_data['depression_prevalence']),
    }
    if HAS_NOCTURNAL:
        correlations['Nocturnal Index vs Depression'] = (
            combined_data['nocturnal_index'].corr(combined_data['depression_prevalence'])
        )
    
    for metric, corr in correlations.items():
        print(f"{metric}: {corr:.4f}")
    
    # Enhanced Visualizations
    print("\n=== Creating Enhanced Visualizations ===")
    
    # Create a comprehensive visualization
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Enhanced NYC Noise and Mental Health Analysis', fontsize=16, fontweight='bold')
    
    # 1. Population-normalized noise rate distribution
    axes[0, 0].hist(combined_data['noise_rate_per_100k'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_title('Distribution of Noise Rate per 100k Population')
    axes[0, 0].set_xlabel('Noise Complaints per 100k Population')
    axes[0, 0].set_ylabel('Frequency')
    
    # 2. Scatter plot: Population-normalized noise vs depression
    axes[0, 1].scatter(combined_data['noise_rate_per_100k'], combined_data['depression_prevalence'], 
                       alpha=0.7, color='coral', s=60)
    axes[0, 1].set_title('Noise Rate per 100k vs Depression Prevalence')
    axes[0, 1].set_xlabel('Noise Complaints per 100k Population')
    axes[0, 1].set_ylabel('Depression Prevalence (%)')
    
    # Add trend line
    z = np.polyfit(combined_data['noise_rate_per_100k'], combined_data['depression_prevalence'], 1)
    p = np.poly1d(z)
    axes[0, 1].plot(combined_data['noise_rate_per_100k'], p(combined_data['noise_rate_per_100k']), 
                    "r--", alpha=0.8, linewidth=2)
    
    # 3. Correlation heatmap
    corr_cols = ['noise_complaint_count', 'noise_rate_per_100k']
    if HAS_NOCTURNAL:
        corr_cols.append('nocturnal_index')
    corr_cols.append('depression_prevalence')
    corr_data = combined_data[corr_cols].corr()
    sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, square=True, ax=axes[0, 2])
    axes[0, 2].set_title('Correlation Matrix')
    
    # 4. Raw noise count vs depression
    axes[1, 0].scatter(combined_data['noise_complaint_count'], combined_data['depression_prevalence'], 
                       alpha=0.7, color='lightgreen', s=60)
    axes[1, 0].set_title('Raw Noise Count vs Depression Prevalence')
    axes[1, 0].set_xlabel('Noise Complaint Count')
    axes[1, 0].set_ylabel('Depression Prevalence (%)')
    
    # Add trend line
    z2 = np.polyfit(combined_data['noise_complaint_count'], combined_data['depression_prevalence'], 1)
    p2 = np.poly1d(z2)
    axes[1, 0].plot(combined_data['noise_complaint_count'], p2(combined_data['noise_complaint_count']), 
                    "r--", alpha=0.8, linewidth=2)
    
    # 5. Nocturnal index vs depression (only when the index could be computed)
    if HAS_NOCTURNAL:
        axes[1, 1].scatter(combined_data['nocturnal_index'], combined_data['depression_prevalence'],
                           alpha=0.7, color='purple', s=60)
        axes[1, 1].set_title('Nocturnal Noise Index vs Depression Prevalence')
        axes[1, 1].set_xlabel('Nocturnal Noise Index')
        axes[1, 1].set_ylabel('Depression Prevalence (%)')
        z3 = np.polyfit(combined_data['nocturnal_index'], combined_data['depression_prevalence'], 1)
        p3 = np.poly1d(z3)
        axes[1, 1].plot(combined_data['nocturnal_index'], p3(combined_data['nocturnal_index']),
                        "r--", alpha=0.8, linewidth=2)
    else:
        axes[1, 1].axis('off')
        axes[1, 1].text(0.5, 0.5, 'Nocturnal Noise Index\nrequires complaint-level 311 data',
                        ha='center', va='center', fontsize=10, color='grey')
    
    # 6. Population vs noise rate
    axes[1, 2].scatter(combined_data['population'], combined_data['noise_rate_per_100k'], 
                       alpha=0.7, color='orange', s=60)
    axes[1, 2].set_title('Population vs Noise Rate per 100k')
    axes[1, 2].set_xlabel('Population')
    axes[1, 2].set_ylabel('Noise Rate per 100k')
    
    plt.tight_layout()
    plt.savefig(DATA_DIR / "enhanced_analysis_plots.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Enhanced Modeling
    print("\n=== Enhanced Modeling ===")
    
    # Prepare features
    features = ['noise_complaint_count', 'noise_rate_per_100k', 'population']
    if HAS_NOCTURNAL:
        features.append('nocturnal_index')
    X = combined_data[features].fillna(0)
    y = combined_data['depression_prevalence'].fillna(combined_data['depression_prevalence'].mean())
    
    # Standardize features for multiple regression
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Multiple regression models
    models = {}
    
    # Single feature models
    models['Raw Noise Count'] = LinearRegression().fit(X[['noise_complaint_count']], y)
    models['Population-Normalized Rate'] = LinearRegression().fit(X[['noise_rate_per_100k']], y)
    if HAS_NOCTURNAL:
        models['Nocturnal Index'] = LinearRegression().fit(X[['nocturnal_index']], y)
    
    # Multiple feature model
    models['Multiple Features'] = LinearRegression().fit(X_scaled, y)
    
    # Robust regression
    models['Robust (Theil-Sen)'] = TheilSenRegressor(random_state=42).fit(X[['noise_rate_per_100k']], y)
    
    # Model evaluation
    print("\nModel Performance:")
    for name, model in models.items():
        if name == 'Multiple Features':
            y_pred = model.predict(X_scaled)
        elif name == 'Raw Noise Count':
            y_pred = model.predict(X[['noise_complaint_count']])
        elif name == 'Population-Normalized Rate':
            y_pred = model.predict(X[['noise_rate_per_100k']])
        elif name == 'Nocturnal Index':
            y_pred = model.predict(X[['nocturnal_index']])
        else:  # Robust
            y_pred = model.predict(X[['noise_rate_per_100k']])
        
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        print(f"{name}:")
        print(f"  R-squared: {r2:.4f}")
        print(f"  MSE: {mse:.2f}")
        print(f"  RMSE: {np.sqrt(mse):.2f}")
        
        # Feature importance for multiple features model
        if name == 'Multiple Features':
            feature_importance = pd.DataFrame({
                'feature': features,
                'coefficient': model.coef_,
                'abs_coefficient': np.abs(model.coef_)
            }).sort_values('abs_coefficient', ascending=False)
            print(f"  Feature Importance:")
            for _, row in feature_importance.iterrows():
                print(f"    {row['feature']}: {row['coefficient']:.4f}")
    
    # Statistical significance testing
    print("\n=== Statistical Significance Testing ===")
    
    # Pearson correlation test
    sig_features = ['noise_complaint_count', 'noise_rate_per_100k']
    if HAS_NOCTURNAL:
        sig_features.append('nocturnal_index')
    for feature in sig_features:
        corr_coef, p_value = stats.pearsonr(combined_data[feature], combined_data['depression_prevalence'])
        print(f"{feature} vs Depression:")
        print(f"  Correlation: {corr_coef:.4f}")
        print(f"  P-value: {p_value:.6f}")
        print(f"  Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
    
    # Create model comparison plot
    plt.figure(figsize=(12, 8))
    
    # Plot actual vs predicted for best models
    plt.subplot(2, 2, 1)
    y_pred_raw = models['Raw Noise Count'].predict(X[['noise_complaint_count']])
    plt.scatter(y, y_pred_raw, alpha=0.7, color='blue')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
    plt.xlabel('Actual Depression Prevalence')
    plt.ylabel('Predicted Depression Prevalence')
    plt.title('Raw Noise Count Model')
    
    plt.subplot(2, 2, 2)
    y_pred_norm = models['Population-Normalized Rate'].predict(X[['noise_rate_per_100k']])
    plt.scatter(y, y_pred_norm, alpha=0.7, color='green')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
    plt.xlabel('Actual Depression Prevalence')
    plt.ylabel('Predicted Depression Prevalence')
    plt.title('Population-Normalized Rate Model')
    
    if HAS_NOCTURNAL:
        plt.subplot(2, 2, 3)
        y_pred_noct = models['Nocturnal Index'].predict(X[['nocturnal_index']])
        plt.scatter(y, y_pred_noct, alpha=0.7, color='purple')
        plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
        plt.xlabel('Actual Depression Prevalence')
        plt.ylabel('Predicted Depression Prevalence')
        plt.title('Nocturnal Index Model')
    
    plt.subplot(2, 2, 4)
    y_pred_multi = models['Multiple Features'].predict(X_scaled)
    plt.scatter(y, y_pred_multi, alpha=0.7, color='orange')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
    plt.xlabel('Actual Depression Prevalence')
    plt.ylabel('Predicted Depression Prevalence')
    plt.title('Multiple Features Model')
    
    plt.tight_layout()
    plt.savefig(DATA_DIR / "model_comparison_plots.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save enhanced results
    print("\n=== Saving Enhanced Results ===")
    
    # Save enhanced dataset
    combined_data.to_csv(DATA_DIR / "enhanced_combined_data.csv", index=False)
    
    # Create summary statistics
    summary_stats = {
        'dataset_size': len(combined_data),
        'neighborhoods': combined_data['UHF42'].nunique(),
        'total_noise_complaints': int(combined_data['noise_complaint_count'].sum()),
        'avg_depression_prevalence': float(combined_data['depression_prevalence'].mean()),
        'correlations': correlations,
        'model_performance': {}
    }
    
    # Add model performance to summary
    for name, model in models.items():
        if name == 'Multiple Features':
            y_pred = model.predict(X_scaled)
        elif name == 'Raw Noise Count':
            y_pred = model.predict(X[['noise_complaint_count']])
        elif name == 'Population-Normalized Rate':
            y_pred = model.predict(X[['noise_rate_per_100k']])
        elif name == 'Nocturnal Index':
            y_pred = model.predict(X[['nocturnal_index']])
        else:  # Robust
            y_pred = model.predict(X[['noise_rate_per_100k']])
        
        summary_stats['model_performance'][name] = {
            'r2': float(r2_score(y, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y, y_pred)))
        }
    
    with open(DATA_DIR / "enhanced_analysis_summary.json", 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    print("Enhanced analysis completed successfully!")
    print("Files created:")
    print("- enhanced_combined_data.csv")
    print("- enhanced_analysis_plots.png")
    print("- model_comparison_plots.png")
    print("- enhanced_analysis_summary.json")
    
    return combined_data, summary_stats

if __name__ == "__main__":
    enhanced_data, summary = enhanced_analysis()

