import tensorflow as tf
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .utils import preprocess_input
from rest_framework.response import Response
from .config import FRAUD_CATEGORY
from rest_framework import status
import os
import io
import numpy as np
import pandas as pd
from loguru import logger

# Load model once when Django starts
model_path = os.path.join(os.path.dirname(__file__), "model.h5")
model = tf.keras.models.load_model(model_path)

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
    Process uploaded CSV/XLS file, append predictions, and return updated file.
    """
    try:
        uploaded_file = request.FILES["file"]
        if not uploaded_file.name.endswith((".csv", ".xls", ".xlsx")):
            return Response({"error": "Only CSV or XLS/XLSX files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Read the uploaded file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Ensure required columns exist
        required_columns = ["policy_no", "assured_age", "policy_sum_assured", "premium", "annual_income", "policy_term", "policy_payment_term", "bank_code"]
        if not all(col in df.columns for col in required_columns):
            return Response({"error": "Missing required columns"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract features and predict
        features = df[required_columns].values
        df["Predicted"] = model.predict(features)  # Append predictions

        # Convert DataFrame back to file
        output = io.BytesIO()
        if uploaded_file.name.endswith(".csv"):
            df.to_csv(output, index=False)
            response = HttpResponse(output.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="predicted_output.csv"'
        else:
            df.to_excel(output, index=False)
            response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = 'attachment; filename="predicted_output.xlsx"'

        return response

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
