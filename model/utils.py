import pandas as pd
import numpy as np
from .config import MEAN_STD, MIN_MAX, ONE_HOT_COLUMNS, LABEL_ENCODINGS

def preprocess_dates(df):
    """
    Preprocesses date columns by converting them to datetime, 
    creating new time difference features, handling missing values, 
    and dropping the original date columns.

    Parameters:
    df (pd.DataFrame): Input DataFrame with date columns.

    Returns:
    pd.DataFrame: Processed DataFrame with new time difference features.
    """
    
    # print(f"Before date processing, shape: {df.shape}")

    df["date_of_death"] = pd.to_datetime(df["date_of_death"], errors='coerce', dayfirst=True)
    df["policy_risk_commencement_date"] = pd.to_datetime(df["policy_risk_commencement_date"], errors='coerce', dayfirst=True)
    df["intimation_date"] = pd.to_datetime(df["intimation_date"], errors='coerce', dayfirst=True)


    # Create new features (time differences in days)
    df["policy_to_death_days"] = (df["date_of_death"] - df["policy_risk_commencement_date"]).dt.days
    df["death_to_intimation_days"] = (df["intimation_date"] - df["date_of_death"]).dt.days
    df["policy_to_intimation_days"] = (df["intimation_date"] - df["policy_risk_commencement_date"]).dt.days

    # Fill missing values with -1
    df.fillna({"policy_to_death_days": -1, "death_to_intimation_days": -1, "policy_to_intimation_days": -1}, inplace=True)

    # Drop original date columns
    df.drop(columns=["policy_risk_commencement_date", "date_of_death", "intimation_date"], inplace=True)

    # print(f"After date processing, shape: {df.shape}")
    
    return df

def preprocess_numerical_columns(df):
    """
    Applies precomputed scaling statistics instead of fitting new scalers on a single-row input.
    """
    # print(f"Before numerical processing, shape: {df.shape}")
    
    # StandardScaler transformation
    for col, (mean, std) in MEAN_STD.items():
        if col in df.columns:
            df[col] = (df[col] - mean) / std

    # MinMaxScaler transformation
    for col, (min_val, max_val) in MIN_MAX.items():
        if col in df.columns:
            df[col] = (df[col] - min_val) / (max_val - min_val)

    df = df.round(3)  # Round to 3 decimal places for consistency

    # print(f"After numerical processing, shape: {df.shape}")
    
    return df


def encode_categorical_features(df, one_hot_columns, label_encodings):
    """
    Applies one-hot encoding and label encoding to the given DataFrame.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - one_hot_columns (dict): Dictionary where keys are column names and values are lists of categories for one-hot encoding.
    - label_encodings (dict): Dictionary where keys are column names and values are mappings for label encoding.
    
    Returns:
    - pd.DataFrame: Transformed DataFrame with categorical features encoded.
    """
    
    # print(f"Before encoding categorical features, shape: {df.shape}")

    # Label Encoding
    for col, mapping in label_encodings.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(-1).astype(int)  # Fill unknown values with -1
    # print(f"after label encoding, shape: {df.shape}") 
    
    list_variable = []
    # One-Hot Encoding
    for col, categories in one_hot_columns.items():
        if col in df.columns:
            for category in categories:
                df[f"{col}_{category}"] = (df[col] == category).astype(int)
            df.drop(columns=[col], inplace=True)
            list_variable.append(col)

    # print(list_variable)   
    # print('shape', len(list_variable))    
    
    # print(f"after one hot encoding, shape: {df.shape}")
    # print(df.columns)      
     
    # print(f"After encoding categorical features, shape: {df.shape}")
    
    return df


# Driver function:
def preprocess_input(data):
    # print("Raw input data:", data)  # Debugging: Print raw input

    # Convert input dict to DataFrame
    df = pd.DataFrame([data])
    # print(f"Initial DataFrame shape: {df.shape}")

    # encode the categorical data
    df = preprocess_dates(df) # preprocess the dates data
    df = preprocess_numerical_columns(df) # preprocess the numerical data
    df = encode_categorical_features(df, ONE_HOT_COLUMNS, LABEL_ENCODINGS) 

    X_input = df.to_numpy()
    X_input = X_input.reshape(1, -1)

    # print(f"Final preprocessed DataFrame shape: {df.shape}")
    # print("Final processed data:\n", df.head())  # Debugging: Show the final DataFrame

    return X_input  
