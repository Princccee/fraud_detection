import streamlit as st
import requests
import datetime as dt

# Streamlit UI
st.title("Fraud Detection System")
st.write("Enter the details below to predict whether the insurance claim is fraudulent.")

# Define API endpoint
API_URL = "http://127.0.0.1:8000/model/predict/"

# Define form fields based on Django model
fields = {
    "policy_no": st.number_input("Policy Number", min_value=0, step=1),
    "assured_age": st.number_input("Assured Age", min_value=0, step=1),
    "nominee_relation": st.text_input("Nominee Relation"),
    "occupation": st.text_input("Occupation"),
    "policy_sum_assured": st.number_input("Policy Sum Assured", min_value=0, step=1),
    "premium": st.number_input("Premium", min_value=0.0, step=0.01),
    "premium_payment_mode": st.text_input("Premium Payment Mode"),
    "annual_income": st.number_input("Annual Income", min_value=0, step=1),
    "holder_marital_status": st.text_input("Marital Status"),
    "indiv_requirement_flag": st.text_input("Individual Requirement Flag"),
    "policy_term": st.number_input("Policy Term", min_value=0, step=1),
    "policy_payment_term": st.number_input("Policy Payment Term", min_value=0, step=1),
    "product_type": st.text_input("Product Type"),
    "channel": st.text_input("Channel"),
    "bank_code": st.number_input("Bank Code", value=0.0, step=0.01),

    "policy_risk_commencement_date": st.date_input("Policy Risk Commencement Date"),
    "date_of_death": st.date_input("Date of Death"),
    "intimation_date": st.date_input("Intimation Date"),

    "status": st.text_input("Status"),
    "sub_status": st.text_input("Sub Status"),
}

# Convert dates to string format
for date_field in ["policy_risk_commencement_date", "date_of_death", "intimation_date"]:
    fields[date_field] = fields[date_field].strftime("%Y-%m-%d") if fields[date_field] else None

# Submit button
if st.button("Predict Fraud"):
    try:
        response = requests.post(API_URL, json=fields)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Prediction: {result['prediction']}")
        else:
            st.error(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
