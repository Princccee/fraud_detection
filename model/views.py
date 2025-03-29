import tensorflow as tf
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import FileUploadSerializer
from .utils import preprocess_input
from .analyse_data import *
from rest_framework.response import Response
from .config import FRAUD_CATEGORY
from rest_framework import status
from django.conf import settings
import base64
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
        # logger.info(f"Received request: {request.method} - {request.body}")
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
        return Response({"prediction": fraud_category}, status=200)    
    
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
    
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def file_upload(request):
    """
    Handles file uploads (CSV or Excel), performs analysis, and returns results.

    Returns:
    - JSON response with average values from analysis and a success message.
    """
    serializer = FileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    file = serializer.validated_data['file']
    file_extension = file.name.split('.')[-1].lower()

    # Read CSV or Excel file
    try:
        if file_extension == 'csv':
            df = pd.read_csv(file)
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(file)
        else:
            return Response({"error": "Unsupported file format"}, status=400)
    except Exception as e:
        return Response({"error": f"Error reading file: {str(e)}"}, status=400)

    # Perform analysis
    avg_values = standard_analysis(df)

    # Get list of images from 'static' folder
    static_folder = os.path.join(settings.BASE_DIR, 'static')
    image_files = [f for f in os.listdir(static_folder) if f.endswith(".jpg")]

    # Convert images to base64
    image_data = {}
    for image_file in image_files:
        image_path = os.path.join(static_folder, image_file)
        with open(image_path, "rb") as img_file:
            image_data[image_file] = base64.b64encode(img_file.read()).decode("utf-8")

    return Response({
        "message": "Analysis completed",
        "Averages": avg_values,
        # "images": image_data  # Contains Base64 encoded images
    }, status=200)