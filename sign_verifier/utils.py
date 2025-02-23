from google.oauth2 import service_account
from googleapiclient.discovery import build
from fraud_detection.settings import GOOGLE_DRIVE_CREDENTIALS

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = GOOGLE_DRIVE_CREDENTIALS  # From settings.py

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=credentials)

def list_drive_files():
    results = drive_service.files().list().execute()
    files = results.get("files", [])
    for file in files:
        print(f"Found file: {file['name']} ({file['id']})")

list_drive_files()
