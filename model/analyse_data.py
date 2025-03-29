import numpy as np
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import seaborn as sns

def get_demographic_info(df, output_dir="static"):
    """
    Generates and saves demographic visualizations for policyholders.

    Parameters:
    df (DataFrame): The DataFrame containing policyholder data.
    output_dir (str): Directory to save the plots.

    Returns:
    None
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 1. Age Distribution of Policyholders
    filename = "Age Distribution of Policyholders.jpg"
    filepath = os.path.join(output_dir, filename)

    plt.figure(figsize=(10, 5))
    sns.histplot(df['assured_age'], bins=20, kde=True, color='blue')
    plt.xlabel("Age of Policyholder")
    plt.ylabel("Frequency")
    plt.title("Age Distribution of Policyholders")
    plt.savefig(filepath, format="jpg", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {filepath}")

    # 2. Marital Status Breakdown of Policyholders
    filename = "Marital Status Breakdown of Policyholders.jpg"
    filepath = os.path.join(output_dir, filename)

    plt.figure(figsize=(6, 6))
    df['holder_marital_status'].value_counts().plot.pie(
        autopct='%1.1f%%', colors=["skyblue", "orange", "green", "red"]
    )
    plt.title("Marital Status Breakdown of Policyholders")
    plt.ylabel("")
    plt.savefig(filepath, format="jpg", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {filepath}")

    # 3. Most Common Occupations Among Policyholders
    filename = "Most Common Occupations Among Policyholders.jpg"
    filepath = os.path.join(output_dir, filename)

    plt.figure(figsize=(10, 5))
    sns.countplot(y=df['occupation'], order=df['occupation'].value_counts().index, palette="viridis")
    plt.xlabel("Number of Policyholders")
    plt.ylabel("Occupation")
    plt.title("Most Common Occupations Among Policyholders")
    plt.savefig(filepath, format="jpg", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {filepath}")
    

def get_average_values(df):
    """
    Calculate the average age of individuals in the DataFrame.
    
    Parameters:
    df (pd.DataFrame): Input DataFrame with 'age' column.
    
    Returns:
    float: Average age.
    """
    avg_values = {}
    columns = ["assured_age", "premium", "annual_income"]

    for col in columns:
        if col in df.columns:
            avg_values[col] = df[col].mean()
        else:
            avg_values[col] = None
    return avg_values

def standard_analysis(df):
    """
    Perform standard analysis on the DataFrame.
    
    Parameters:
    df (pd.DataFrame): Input DataFrame.
    
    Returns:
    dict: A dictionary containing summary statistics and a confusion matrix plot.
    """
    
    avg_values = get_average_values(df)
    get_demographic_info(df)
    
    return avg_values
