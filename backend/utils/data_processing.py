import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_data(df):
    """
    Perform comprehensive data cleaning
    """
    try:
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_rows:
            logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing values
        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                # For numerical columns, fill with median instead of mean for robustness
                df[column] = df[column].fillna(df[column].median())
            else:
                # For categorical columns, fill with mode or 'Unknown'
                mode_value = df[column].mode()
                if not mode_value.empty:
                    df[column] = df[column].fillna(mode_value[0])
                else:
                    df[column] = df[column].fillna('Unknown')
        
        # Remove outliers using IQR method for numerical columns
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        if len(numerical_columns) > 0:
            for column in numerical_columns:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers_count = len(df[(df[column] < lower_bound) | (df[column] > upper_bound)])
                if outliers_count > 0:
                    logger.info(f"Removing {outliers_count} outliers from column {column}")
                df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        
        return df
    except Exception as e:
        logger.error(f"Error in clean_data: {str(e)}")
        raise Exception(f"Failed to clean data: {str(e)}")

def normalize_data(df):
    """
    Normalize numerical data
    """
    try:
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        if len(numerical_columns) > 0:
            scaler = StandardScaler()
            df[numerical_columns] = scaler.fit_transform(df[numerical_columns])
        else:
            logger.warning("No numerical columns found for normalization")
        return df
    except Exception as e:
        logger.error(f"Error in normalize_data: {str(e)}")
        raise Exception(f"Failed to normalize data: {str(e)}")

def encode_categorical_data(df):
    """
    Encode categorical variables
    """
    try:
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            le = LabelEncoder()
            for column in categorical_columns:
                df[column] = le.fit_transform(df[column].astype(str))
        else:
            logger.warning("No categorical columns found for encoding")
        return df
    except Exception as e:
        logger.error(f"Error in encode_categorical_data: {str(e)}")
        raise Exception(f"Failed to encode categorical data: {str(e)}")

def detect_data_types(df):
    """
    Detect and suggest appropriate data types for columns
    """
    type_info = {}
    for column in df.columns:
        dtype = df[column].dtype
        if dtype in ['int64', 'float64']:
            type_info[column] = 'numerical'
        elif dtype == 'object':
            # Check if it's a date
            try:
                pd.to_datetime(df[column].iloc[0])
                type_info[column] = 'datetime'
            except:
                # Check if it's boolean-like
                unique_values = df[column].unique()
                if len(unique_values) == 2 and set(unique_values).issubset({0, 1, 'True', 'False', 'true', 'false', 'Yes', 'No', 'yes', 'no'}):
                    type_info[column] = 'boolean'
                else:
                    type_info[column] = 'categorical'
        else:
            type_info[column] = str(dtype)
    return type_info

def generate_summary_stats(df):
    """
    Generate comprehensive summary statistics
    """
    try:
        stats = {
            'shape': df.shape,
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'detected_types': detect_data_types(df),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicates': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        # Add numerical summary only if there are numerical columns
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        if len(numerical_columns) > 0:
            stats['numerical_summary'] = df.describe().to_dict()
        
        # Add categorical summary only if there are categorical columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            categorical_summary = {}
            for col in categorical_columns:
                value_counts = df[col].value_counts()
                categorical_summary[col] = {
                    'unique_values': len(value_counts),
                    'top_values': value_counts.head(5).to_dict()
                }
            stats['categorical_summary'] = categorical_summary
        
        return stats
    except Exception as e:
        logger.error(f"Error in generate_summary_stats: {str(e)}")
        raise Exception(f"Failed to generate summary statistics: {str(e)}")