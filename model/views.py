import tensorflow as tf
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import preprocess_input, parse_signature_result, frogery_test
from rest_framework.response import Response
from .config import FRAUD_CATEGORY
from rest_framework import status
from django.conf import settings
from django.http import FileResponse, Http404
from gradio_client import Client, handle_file
import requests
import tempfile
import os
import re
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
    

@api_view(["GET"])
def download_file(request):
    """
    Serve the processed file from the predicted_output folder for download.
    """
    try:
        file_path_csv = os.path.join(UPLOAD_DIR, "predicted_output.csv")
        file_path_excel = os.path.join(UPLOAD_DIR, "predicted_output.xlsx")

        # Choose which file exists (CSV or Excel)
        if os.path.exists(file_path_csv):
            file_path = file_path_csv
            content_type = 'text/csv'
        elif os.path.exists(file_path_excel):
            file_path = file_path_excel
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            raise FileNotFoundError("No processed file found to download.")

        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response

    except FileNotFoundError as fnf_error:
        return Response({"error": str(fnf_error)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    

# def parse_signature_result(result_list: list | tuple) -> dict:
#     if not result_list or not isinstance(result_list, (list, tuple)):
#         return {"Similarity score": "N/A", "Result": "N/A"}

#     text = result_list[0]  # the text containing score and match result

#     # Extract similarity score
#     score_match = re.search(r"Similarity Score:\s*([\d.]+%)", text)
#     similarity_score = score_match.group(1) if score_match else "N/A"

#     # Extract match result
#     result_match = re.search(r"(Matched|Not Matched|Manual Check Recommended)", text, re.IGNORECASE)
#     result = result_match.group(1).capitalize() if result_match else "N/A"

#     return {
#         "Similarity score": similarity_score,
#         "Result": result
#     }

# def frogery_test(image_file, reference_number):
#     # Create a temporary file to save the uploaded image
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
#         for chunk in image_file.chunks():
#             tmp.write(chunk)
#         tmp_path = tmp.name

#     try:
#         # Initialize Gradio Client
#         client = Client("786avinash/signatureapi")

#         # Call Gradio API with the uploaded image and reference number
#         result = client.predict(
#             document_image=handle_file(tmp_path),
#             reference_number=reference_number,
#             api_name="/predict"
#         )
#         return result

#     finally:
#         # Clean up temp file
#         os.remove(tmp_path)

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])  # Handle form data with file uploads
def verify_signature(request):
    """
    Accepts an image and a reference number,
    calls the Gradio API via frogery_test, and returns the result.
    """
    try:
        image_file = request.FILES.get('image')
        reference_number = request.data.get('reference_number')

        if not image_file or not reference_number:
            return Response({'error': 'Image and reference_number are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reference_number = int(reference_number)
        except ValueError:
            return Response({'error': 'reference_number must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        # Call the function
        result = frogery_test(image_file, reference_number)
        print("Raw API result:", result)
        parsed_result = parse_signature_result(result)
        print("Parsed result: ", parsed_result)
        return Response(parsed_result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in verify_signature: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
