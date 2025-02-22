import tensorflow as tf
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .utils import preprocess_input
from rest_framework.response import Response
from .config import FRAUD_CATEGORY
from rest_framework import status
from django.conf import settings
import os
import io
import numpy as np
import pandas as pd
from loguru import logger

# Load model once when Django starts
model_path = os.path.join(os.path.dirname(__file__), "model.h5")
model = tf.keras.models.load_model(model_path)

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "predicted_files") 

@api_view(["POST"])
def predict_json(request):
    """
    API to receive input data, preprocess it, and return model predictions.
    """
    try:
        input_data = request.data  # Get JSON data from request
        
        # Step 1: Preprocess input using utils.py
        processed_data = preprocess_input(input_data)
        # print("processed data: ",processed_data)

        # Step 2: Predict using the pre-trained model
        predictions = model.predict(processed_data)

        # Step 3: Convert predictions to a readable format
        predicted_class = int(np.argmax(predictions, axis=1)[0])
        # print("predicted class: ", predicted_class)

        fraud_category = FRAUD_CATEGORY[predicted_class]

        return Response({"prediction": fraud_category})
    
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
def predict_file(request):
    """
    Upload a CSV/XLS file, preprocess it, generate predictions,
    save the processed file, and return it to the frontend.
    """
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Get the uploaded file
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file format
        if not uploaded_file.name.endswith((".csv", ".xls", ".xlsx")):
            return Response({"error": "Only CSV or XLS/XLSX files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Read the file into a DataFrame
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Ensure required columns exist
        required_columns = [
            "assured_age", "nominee_relation", "occupation", "policy_sum_assured", "premium",
            "premium_payment_mode", "annual_income", "holder_marital_status", "indiv_requirement_flag",
            "policy_term", "policy_payment_term", "product_type", "channel", "bank_code",
            "policy_risk_commencement_date", "date_of_death", "intimation_date", "status", "sub_status"
        ]

        if not all(col in df.columns for col in required_columns):
            return Response({"error": "Missing required columns"}, status=status.HTTP_400_BAD_REQUEST)

        # Process each row and generate predictions
        predictions = []
        for _, row in df.iterrows():
            processed_input = preprocess_input(row.to_dict())  # Preprocess the row

            # final_features = get_final_features(processed_input)  # Get final array of values

            prediction = model.predict(processed_input)  # Model outputs an integer
            predicted_class = int(np.argmax(prediction, axis=1)[0])

            fraud_category = FRAUD_CATEGORY[predicted_class]
            
            predictions.append(fraud_category)  # Append category name

        # Append fraud category predictions to DataFrame
        df["Predicted"] = predictions

        # Save the processed file
        file_extension = ".csv" if uploaded_file.name.endswith(".csv") else ".xlsx"
        output_filename = os.path.join(UPLOAD_DIR, f"predicted_output{file_extension}")

        if file_extension == ".csv":
            df.to_csv(output_filename, index=False)
        else:
            df.to_excel(output_filename, index=False)

        # Return JSON response
        return Response({"message": "Successfully processed the file"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    