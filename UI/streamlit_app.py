import streamlit as st
import requests
import datetime as dt
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.config import ONE_HOT_COLUMNS, LABEL_ENCODINGS

# Streamlit UI
st.title("Fraud Detection System")
st.write("Enter the details below to predict whether the insurance claim is fraudulent.")

# Define API endpoint
API_URL = "https://frauddetection-production-40cd.up.railway.app/model/predict/"
API_FILE_URL = "https://frauddetection-production-40cd.up.railway.app/model/predict_file/"

# Define form fields
fields = {
    # "policy_no": st.number_input("Policy Number", min_value=0, step=1),
    "assured_age": st.number_input("Assured Age", min_value=0, step=1),
    "nominee_relation": st.selectbox("Nominee Relation", options=list(LABEL_ENCODINGS['nominee_relation'].keys())),
    "occupation": st.selectbox("Occupation", options=list(LABEL_ENCODINGS['occupation'].keys())),
    "policy_sum_assured": st.number_input("Policy Sum Assured", min_value=0, step=1),
    "premium": st.number_input("Premium", min_value=0.0, step=0.01),
    "premium_payment_mode": st.selectbox("Premium Payment Mode", options=ONE_HOT_COLUMNS['premium_payment_mode']),
    "annual_income": st.number_input("Annual Income", min_value=0, step=1),
    "holder_marital_status": st.selectbox("Marital Status", options=ONE_HOT_COLUMNS['holder_marital_status']),
    "indiv_requirement_flag": st.selectbox("Individual Requirement Flag", options=ONE_HOT_COLUMNS['indiv_requirement_flag']),
    "policy_term": st.number_input("Policy Term", min_value=0, step=1),
    "policy_payment_term": st.number_input("Policy Payment Term", min_value=0, step=1),
    "product_type": st.selectbox("Product Type", options=ONE_HOT_COLUMNS['product_type']),
    "channel": st.selectbox("Channel", options=ONE_HOT_COLUMNS['channel']),
    "bank_code": st.number_input("Bank Code", value=0.0, step=0.01),
    "policy_risk_commencement_date": st.date_input("Policy Risk Commencement Date"),
    "date_of_death": st.date_input("Date of Death"),
    "intimation_date": st.date_input("Intimation Date"),
    "status": st.selectbox("Status", options=LABEL_ENCODINGS['status']),
    "sub_status": st.selectbox("Sub Status", options=LABEL_ENCODINGS['sub_status']),
}

# Convert dates to string format
for date_field in ["policy_risk_commencement_date", "date_of_death", "intimation_date"]:
    fields[date_field] = fields[date_field].strftime("%Y-%m-%d") if fields[date_field] else None

# Submit button for single prediction
if st.button("Predict Fraud"):
    try:
        response = requests.post(API_URL, json=fields, timeout=30)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Prediction: {result.get('prediction', 'Unknown')}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

st.write("---")

# File upload for batch processing
st.subheader("Upload a CSV/XLS file for batch fraud detection")
uploaded_file = st.file_uploader("Upload your CSV or XLS file", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    st.write("File uploaded successfully!")
    if st.button("Predict Fraud for File"):
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(API_FILE_URL, files=files, timeout=60)
            if response.status_code == 200:
                result = response.json()
                st.success("Batch prediction completed. Download the results below.")
                st.download_button("Download Results", data=str(result), file_name="fraud_predictions.json", mime="application/json")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

