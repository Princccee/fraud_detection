import os
import uuid
from django.http import JsonResponse
from rest_framework.decorators import api_view
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from gradio_client import Client
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Load environment variables
GOOGLE_DRIVE_FOLDER_ID = "your_google_drive_folder_id"
SERVICE_ACCOUNT_FILE = "service_account.json"

# Authenticate Google Drive API
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"])
drive_service = build("drive", "v3", credentials=creds)

# Function to upload image to Google Drive
def upload_to_drive(image_path, filename):
    file_metadata = {
        "name": filename,
        "parents": [GOOGLE_DRIVE_FOLDER_ID]
    }
    media = {"mimeType": "image/png"}
    file = drive_service.files().create(body=file_metadata, media_body=image_path, fields="id").execute()

    # Make file public
    drive_service.permissions().create(fileId=file["id"], body={"role": "reader", "type": "anyone"}).execute()

    # Get public URL
    return f"https://drive.google.com/uc?id={file['id']}"

@api_view(["POST"])
def upload_image(request):
    if "image" not in request.FILES or "app_number" not in request.data:
        return JsonResponse({"error": "Missing image or app_number"}, status=400)

    image = request.FILES["image"]
    app_number = request.data["app_number"]

    # Save image temporarily
    filename = f"{uuid.uuid4()}_{image.name}"
    temp_path = default_storage.save(filename, ContentFile(image.read()))

    # Upload to Google Drive
    public_url = upload_to_drive(temp_path, filename)

    # Delete temporary file
    default_storage.delete(temp_path)

    # Call Gradio API
    client = Client("786avinash/signatureapi")
    result = client.predict(
        document_image={"url": public_url},  
        reference_number=float(app_number),  
        api_name="/predict"
    )

    return JsonResponse({
        "verification_result": result[0],
        "signature_image_url": result[1]["url"]
    })
