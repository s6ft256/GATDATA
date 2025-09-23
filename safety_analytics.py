import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz, process

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        # Try to get existing app
        app = firebase_admin.get_app()
    except ValueError:
        # Initialize if not exists
        # Use service account key from environment variable
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            # Fallback to default credentials
            cred = credentials.ApplicationDefault()
        app = firebase_admin.initialize_app(cred)
    return firestore.client()

# Fetch data from Firestore collections
def fetch_firestore_data(db, collection_names):
    """
    Fetch data from specified Firestore collections
    """
    data = {}
    for collection_name in collection_names:
        try:
            docs = db.collection(collection_name).stream()
            collection_data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                collection_data.append(doc_data)
            data[collection_name] = pd.DataFrame(collection_data)
        except Exception as e:
            print(f"Error fetching data from {collection_name}: {str(e)}")
            data[collection_name] = pd.DataFrame()
    return data

# Correlation analysis between different safety datasets
def perform_correlation_analysis(data_dict):
    """
    Perform correlation analysis between different safety datasets
    """
    results = {}
    
    # Combine all dataframes to check for correlations across collections
    combined_df = pd.DataFrame()
    for collection_name, df in data_dict.items():
        if not df.empty:
            # Add prefix to columns to identify source
            df_prefixed = df.add_prefix(f"{collection_name}_")
            if combined_df.empty:
                combined_df = df_prefixed
            else:
                # Merge on index (document ID) if possible
                combined_df = pd.concat([combined_df, df_prefixed], axis=1)
    
    # Select only numeric columns for correlation analysis
    numeric_df = combined_df.select_dtypes(include=[np.number])
    
    if not numeric_df.empty and numeric_df.shape[1] > 1:
        # Calculate correlation matrix
        correlation_matrix = numeric_df.corr()
        
        # Find strong correlations (above 0.7 or below -0.7)
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'variable1': correlation_matrix.columns[i],
                        'variable2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        results['correlation_matrix'] = correlation_matrix.to_dict()
        results['strong_correlations'] = strong_correlations
        
        # Additional analysis: Find correlations between different collection types
        collection_correlations = {}
        for collection1 in data_dict.keys():
            for collection2 in data_dict.keys():
                if collection1 != collection2:
                    # Get columns for each collection
                    cols1 = [col for col in correlation_matrix.columns if col.startswith(f"{collection1}_")]
                    cols2 = [col for col in correlation_matrix.columns if col.startswith(f"{collection2}_")]
                    
                    # Find cross-correlations
                    cross_correlations = []
                    for col1 in cols1:
                        for col2 in cols2:
                            if col1 in correlation_matrix.index and col2 in correlation_matrix.columns:
                                corr_val = correlation_matrix.loc[col1, col2]
                                if abs(corr_val) > 0.5:  # Lower threshold for cross-collection correlations
                                    cross_correlations.append({
                                        'variable1': col1,
                                        'variable2': col2,
                                        'correlation': corr_val
                                    })
                    
                    if cross_correlations:
                        collection_correlations[f"{collection1}_vs_{collection2}"] = cross_correlations
        
        results['collection_correlations'] = collection_correlations
    
    return results

# Root cause analysis using near-miss reports and incident data
def perform_root_cause_analysis(incidents_df, near_miss_df, maintenance_df, audit_df=None, violations_df=None):
    """
    Perform root cause analysis by tracing incident precursors
    """
    results = {}
    
    if not incidents_df.empty:
        # Analyze incident patterns
        results['total_incidents'] = len(incidents_df)
        
        # Look for common factors in incidents
        if 'location' in incidents_df.columns:
            location_counts = incidents_df['location'].value_counts()
            results['incident_locations'] = location_counts.to_dict()
        
        if 'department' in incidents_df.columns:
            department_counts = incidents_df['department'].value_counts()
            results['incident_departments'] = department_counts.to_dict()
        
        # Time-based analysis
        date_columns = [col for col in incidents_df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_columns:
            date_col = date_columns[0]
            try:
                incidents_df[date_col] = pd.to_datetime(incidents_df[date_col])
                incidents_df['incident_month'] = incidents_df[date_col].dt.to_period('M')
                monthly_incidents = incidents_df['incident_month'].value_counts().sort_index()
                results['monthly_incident_trend'] = monthly_incidents.to_dict()
            except:
                pass
        
        # Severity analysis
        severity_columns = [col for col in incidents_df.columns if 'severity' in col.lower() or 'level' in col.lower()]
        if severity_columns:
            severity_col = severity_columns[0]
            severity_counts = incidents_df[severity_col].value_counts()
            results['incident_severity_distribution'] = severity_counts.to_dict()
        
        # If we have near-miss data, compare patterns
        if not near_miss_df.empty and 'location' in near_miss_df.columns and 'location' in incidents_df.columns:
            near_miss_locations = near_miss_df['location'].value_counts()
            incident_locations = incidents_df['location'].value_counts()
            
            # Find locations with both near-misses and incidents
            common_locations = set(near_miss_locations.index) & set(incident_locations.index)
            results['locations_with_near_misses_and_incidents'] = list(common_locations)
            
            # Calculate near-miss to incident ratio
            location_ratios = {}
            for location in common_locations:
                near_miss_count = near_miss_locations.get(location, 0)
                incident_count = incident_locations.get(location, 0)
                if incident_count > 0:
                    ratio = near_miss_count / incident_count
                    location_ratios[location] = ratio
            results['near_miss_to_incident_ratios'] = location_ratios
        
        # If we have maintenance data, check for maintenance-related incidents
        if not maintenance_df.empty:
            # This would require linking maintenance records to incidents
            # For now, we'll just note that both datasets exist
            results['maintenance_data_available'] = True
        
        # If we have audit data, check for compliance-related incidents
        if audit_df is not None and not audit_df.empty:
            results['audit_data_available'] = True
            
            # Look for non-compliance findings
            non_compliance_cols = [col for col in audit_df.columns if 'compliance' in col.lower() or 'finding' in col.lower()]
            if non_compliance_cols:
                nc_col = non_compliance_cols[0]
                non_compliance_count = len(audit_df[audit_df[nc_col].str.lower().str.contains('non', na=False)])
                results['audit_non_compliance_findings'] = non_compliance_count
        
        # If we have violations data, check for violation-related incidents
        if violations_df is not None and not violations_df.empty:
            results['violations_data_available'] = True
            results['total_violations'] = len(violations_df)
    
    return results

# Predictive forecasting for risk levels
def perform_predictive_forecasting(incidents_df, inspections_df, trainings_df, maintenance_df=None, environmental_df=None):
    """
    Perform predictive forecasting using historical data
    """
    results = {}
    
    # Enhanced risk scoring model using multiple factors
    risk_factors = {}
    
    if not incidents_df.empty:
        # Incident-based risk factors
        risk_factors['incident_count'] = len(incidents_df)
        
        # Severity-based risk factors
        severity_columns = [col for col in incidents_df.columns if 'severity' in col.lower() or 'level' in col.lower()]
        if severity_columns:
            severity_col = severity_columns[0]
            high_severity_count = len(incidents_df[incidents_df[severity_col].str.lower().str.contains('high|critical', na=False)])
            risk_factors['high_severity_incidents'] = high_severity_count
        
        # Time-based risk factors
        date_columns = [col for col in incidents_df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_columns:
            date_col = date_columns[0]
            try:
                incidents_df[date_col] = pd.to_datetime(incidents_df[date_col])
                
                # Calculate incident frequency (incidents per month)
                incidents_df['incident_month'] = incidents_df[date_col].dt.to_period('M')
                monthly_incidents = incidents_df['incident_month'].value_counts()
                if len(monthly_incidents) > 1:
                    avg_monthly_incidents = monthly_incidents.mean()
                    risk_factors['avg_monthly_incidents'] = avg_monthly_incidents
                    
                    # Trend analysis - increasing or decreasing
                    if len(monthly_incidents) >= 3:
                        recent_months = monthly_incidents.sort_index().tail(3)
                        trend = 'stable'
                        if len(recent_months) >= 2:
                            if recent_months.iloc[-1] > recent_months.iloc[-2] * 1.1:  # 10% increase
                                trend = 'increasing'
                            elif recent_months.iloc[-1] < recent_months.iloc[-2] * 0.9:  # 10% decrease
                                trend = 'decreasing'
                        risk_factors['incident_trend'] = trend
                
                # Group by time period (e.g., month) to create time series
                incidents_ts = incidents_df.set_index(date_col).resample('M').size()
                
                # Create features for forecasting
                if len(incidents_ts) > 3:  # Need at least 3 data points
                    # Create lag features
                    df_ts = pd.DataFrame({'incidents': incidents_ts.values})
                    df_ts['lag1'] = df_ts['incidents'].shift(1)
                    df_ts['lag2'] = df_ts['incidents'].shift(2)
                    df_ts['lag3'] = df_ts['incidents'].shift(3)
                    
                    # Drop rows with NaN values
                    df_ts = df_ts.dropna()
                    
                    if len(df_ts) > 1:
                        # Prepare features and target
                        X = df_ts[['lag1', 'lag2', 'lag3']]
                        y = df_ts['incidents']
                        
                        # Split data
                        if len(df_ts) > 4:
                            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                        else:
                            X_train, y_train = X, y
                            X_test, y_test = X.iloc[[-1]], y.iloc[[-1]]
                        
                        # Train model
                        model = RandomForestRegressor(n_estimators=100, random_state=42)
                        model.fit(X_train, y_train)
                        
                        # Make predictions
                        if len(X_test) > 0:
                            predictions = model.predict(X_test)
                            mse = mean_squared_error(y_test, predictions)
                            r2 = r2_score(y_test, predictions)
                            
                            # Predict next 3 months
                            last_values = df_ts[['lag1', 'lag2', 'lag3']].iloc[-1:].values
                            future_predictions = []
                            current_values = last_values[0].tolist()
                            
                            for i in range(3):
                                pred = model.predict([current_values])[0]
                                future_predictions.append(max(0, pred))  # Ensure non-negative
                                # Update values for next prediction
                                current_values = [pred] + current_values[:-1]
                            
                            results['forecasting_model'] = {
                                'mse': mse,
                                'r2_score': r2,
                                'future_predictions': future_predictions,
                                'time_periods': ['Month 1', 'Month 2', 'Month 3']
                            }
            except Exception as e:
                print(f"Error in time series conversion: {str(e)}")
    
    # Inspection-based risk factors
    if not inspections_df.empty:
        risk_factors['inspection_count'] = len(inspections_df)
        
        # Compliance-based risk factors
        compliance_columns = [col for col in inspections_df.columns if 'compliance' in col.lower() or 'status' in col.lower()]
        if compliance_columns:
            compliance_col = compliance_columns[0]
            non_compliant_count = len(inspections_df[inspections_df[compliance_col].str.lower().str.contains('non', na=False)])
            risk_factors['non_compliant_inspections'] = non_compliant_count
    
    # Training-based risk factors
    if not trainings_df.empty:
        risk_factors['training_count'] = len(trainings_df)
        
        # Training completion risk factors
        completion_columns = [col for col in trainings_df.columns if 'complet' in col.lower() or 'status' in col.lower()]
        if completion_columns:
            completion_col = completion_columns[0]
            incomplete_count = len(trainings_df[~trainings_df[completion_col].str.lower().str.contains('complet', na=False)])
            risk_factors['incomplete_trainings'] = incomplete_count
    
    # Calculate composite risk score
    composite_risk_score = 0
    
    # Incident-related factors (weight: 40%)
    if 'incident_count' in risk_factors:
        composite_risk_score += risk_factors['incident_count'] * 0.4
    if 'high_severity_incidents' in risk_factors:
        composite_risk_score += risk_factors['high_severity_incidents'] * 2  # Higher weight for high severity
    
    # Inspection-related factors (weight: 30%)
    if 'non_compliant_inspections' in risk_factors:
        composite_risk_score += risk_factors['non_compliant_inspections'] * 0.3
    
    # Training-related factors (weight: 20%)
    if 'incomplete_trainings' in risk_factors:
        composite_risk_score += risk_factors['incomplete_trainings'] * 0.2
    
    # Trend factors (weight: 10%)
    if risk_factors.get('incident_trend') == 'increasing':
        composite_risk_score *= 1.2  # Increase risk score if trend is increasing
    elif risk_factors.get('incident_trend') == 'decreasing':
        composite_risk_score *= 0.8  # Decrease risk score if trend is decreasing
    
    results['current_risk_score'] = composite_risk_score
    
    # Risk level classification
    if composite_risk_score < 20:
        risk_level = "Low"
    elif composite_risk_score < 50:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    results['risk_level'] = risk_level
    results['risk_factors'] = risk_factors
    
    return results

# Compliance scorecard generation
def generate_compliance_scorecard(inspections_df, trainings_df):
    """
    Generate compliance scorecard based on inspection results and training completion
    """
    results = {}
    
    if not inspections_df.empty:
        # Calculate compliance based on inspection results
        total_inspections = len(inspections_df)
        results['total_inspections'] = total_inspections
        
        # Look for compliance status columns
        compliance_columns = [col for col in inspections_df.columns if 'compliance' in col.lower() or 'status' in col.lower()]
        
        if compliance_columns:
            # Assume first compliance column contains pass/fail or compliant/non-compliant values
            compliance_col = compliance_columns[0]
            if compliance_col in inspections_df.columns:
                # Count compliant vs non-compliant
                compliant_count = len(inspections_df[inspections_df[compliance_col].str.lower().str.contains('complian', na=False)])
                non_compliant_count = total_inspections - compliant_count
                
                compliance_rate = (compliant_count / total_inspections) * 100 if total_inspections > 0 else 0
                
                results['compliance_rate'] = compliance_rate
                results['compliant_inspections'] = compliant_count
                results['non_compliant_inspections'] = non_compliant_count
    
    if not trainings_df.empty:
        # Calculate training completion rates
        total_trainings = len(trainings_df)
        results['total_trainings'] = total_trainings
        
        # Look for completion status columns
        completion_columns = [col for col in trainings_df.columns if 'complet' in col.lower() or 'status' in col.lower()]
        
        if completion_columns:
            completion_col = completion_columns[0]
            if completion_col in trainings_df.columns:
                # Count completed vs incomplete
                completed_count = len(trainings_df[trainings_df[completion_col].str.lower().str.contains('complet', na=False)])
                incomplete_count = total_trainings - completed_count
                
                completion_rate = (completed_count / total_trainings) * 100 if total_trainings > 0 else 0
                
                results['training_completion_rate'] = completion_rate
                results['completed_trainings'] = completed_count
                results['incomplete_trainings'] = incomplete_count
    
    return results

# Comparative benchmarking across teams/locations
def perform_benchmarking_analysis(incidents_df, inspections_df, trainings_df):
    """
    Perform comparative benchmarking across teams/locations
    """
    results = {}
    
    # Analyze incidents by department/location
    if not incidents_df.empty:
        # Department analysis
        if 'department' in incidents_df.columns:
            dept_incidents = incidents_df['department'].value_counts()
            results['incidents_by_department'] = dept_incidents.to_dict()
        
        # Location analysis
        if 'location' in incidents_df.columns:
            location_incidents = incidents_df['location'].value_counts()
            results['incidents_by_location'] = location_incidents.to_dict()
    
    # Analyze inspections by department/location
    if not inspections_df.empty:
        # Department analysis
        if 'department' in inspections_df.columns:
            dept_inspections = inspections_df['department'].value_counts()
            results['inspections_by_department'] = dept_inspections.to_dict()
        
        # Location analysis
        if 'location' in inspections_df.columns:
            location_inspections = inspections_df['location'].value_counts()
            results['inspections_by_location'] = location_inspections.to_dict()
    
    # Analyze trainings by department
    if not trainings_df.empty:
        # Department analysis
        if 'department' in trainings_df.columns:
            dept_trainings = trainings_df['department'].value_counts()
            results['trainings_by_department'] = dept_trainings.to_dict()
    
    return results

# Main function to run all analytics
def run_safety_analytics():
    """
    Main function to run all safety analytics and save results
    """
    # Initialize Firestore
    db = initialize_firebase()
    
    # Define collection names for core safety data
    core_collections = ['Incidents', 'Inspections', 'Trainings']
    
    # Define collection names for extended analytics
    extended_collections = [
        'Maintenance Records', 
        'Near-Miss Reports', 
        'Safety Violations', 
        'Audit Results', 
        'Environmental Conditions', 
        'Equipment Logs'
    ]
    
    # Fetch data from all collections
    all_collections = core_collections + extended_collections
    data = fetch_firestore_data(db, all_collections)
    
    # Separate core and extended data
    core_data = {k: v for k, v in data.items() if k in core_collections}
    extended_data = {k: v for k, v in data.items() if k in extended_collections}
    
    # Initialize results dictionary
    analytics_results = {
        'timestamp': datetime.now().isoformat(),
        'core_collections_analyzed': list(core_data.keys()),
        'extended_collections_analyzed': list(extended_data.keys())
    }
    
    # Run correlation analysis
    print("Running correlation analysis...")
    correlation_results = perform_correlation_analysis(core_data)
    analytics_results['correlation_analysis'] = correlation_results
    
    # Run root cause analysis
    print("Running root cause analysis...")
    incidents_df = core_data.get('Incidents', pd.DataFrame())
    near_miss_df = data.get('Near-Miss Reports', pd.DataFrame())
    maintenance_df = data.get('Maintenance Records', pd.DataFrame())
    audit_df = data.get('Audit Results', pd.DataFrame())
    violations_df = data.get('Safety Violations', pd.DataFrame())
    root_cause_results = perform_root_cause_analysis(incidents_df, near_miss_df, maintenance_df, audit_df, violations_df)
    analytics_results['root_cause_analysis'] = root_cause_results
    
    # Run predictive forecasting
    print("Running predictive forecasting...")
    inspections_df = core_data.get('Inspections', pd.DataFrame())
    trainings_df = core_data.get('Trainings', pd.DataFrame())
    maintenance_df = data.get('Maintenance Records', pd.DataFrame())
    environmental_df = data.get('Environmental Conditions', pd.DataFrame())
    forecasting_results = perform_predictive_forecasting(incidents_df, inspections_df, trainings_df, maintenance_df, environmental_df)
    analytics_results['predictive_forecasting'] = forecasting_results
    
    # Generate compliance scorecard
    print("Generating compliance scorecard...")
    compliance_results = generate_compliance_scorecard(inspections_df, trainings_df)
    analytics_results['compliance_scorecard'] = compliance_results
    
    # Perform benchmarking analysis
    print("Performing benchmarking analysis...")
    benchmarking_results = perform_benchmarking_analysis(incidents_df, inspections_df, trainings_df)
    analytics_results['benchmarking_analysis'] = benchmarking_results
    
    # Save results to file
    try:
        with open('safety_analytics_results.json', 'w') as f:
            json.dump(analytics_results, f, indent=2, default=str)
        print("Analytics results saved to safety_analytics_results.json")
    except Exception as e:
        print(f"Error saving analytics results: {str(e)}")
    
    return analytics_results

# Function to get analytics results for the dashboard
def get_analytics_for_dashboard():
    """
    Get analytics results in a format suitable for the React dashboard
    """
    try:
        with open('safety_analytics_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, run analytics first
        results = run_safety_analytics()
        return results
    except Exception as e:
        print(f"Error loading analytics results: {str(e)}")
        return {}

if __name__ == "__main__":
    # Run the analytics
    results = run_safety_analytics()
    print("Safety analytics completed successfully!")