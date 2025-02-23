import gdown
import cv2
import numpy as np
import gradio as gr
import matplotlib.pyplot as plt
from gradio_client import Client, handle_file

# ✅ Dictionary of public Google Drive links for reference signatures
drive_links = {
    1: "https://drive.google.com/file/d/1xtzL6-TpN4EVyaFUF4MM4ssjAZqZutF8/view?usp=drive_link",
    2: "https://drive.google.com/file/d/1UpPfOlDXoWwB5Ub530uhUrOVnUnWYvpQ/view?usp=drive_link",
    3: "https://drive.google.com/file/d/1-M_PND4PK3tSLY705olnsswOk5bNoOFa/view?usp=drive_link",
    4: "https://drive.google.com/file/d/1FL1uLEXlWW-nQYNoaBARiVs0N0XAwsvW/view?usp=drive_link",
    5: "https://drive.google.com/file/d/1nZhl1CkvuH-KA4ErAslD-91W2QnBajhx/view?usp=drive_link",
    6: "https://drive.google.com/file/d/1SHEgykTZN9lGdDaR6PTl9P01-Zlpu6cZ/view?usp=drive_link",
    7: "https://drive.google.com/file/d/1gRE9SmvT7OBw8JYCyx7ehMs3lBpiX-Bp/view?usp=drive_link"
}

# ✅ Function to extract file ID from Google Drive link
def extract_file_id(drive_url):
    return drive_url.split("/d/")[1].split("/view")[0]

# ✅ Function to download a file from Google Drive
def download_from_drive(file_id, save_path):
    gdown.download(f"https://drive.google.com/uc?id={file_id}", save_path, quiet=False)
    return save_path

# ✅ Function to extract the signature from a document image
def extract_signature(document_image_path):
    client = Client("tech4humans/signature-detection")
    result = client.predict(
        image=handle_file(document_image_path),
        conf_thres=0.25,
        iou_thres=0.5,
        api_name="/process_image"
    )

    extracted_signature_info = result[0]
    extracted_signature_path = (
        extracted_signature_info.get("path") if isinstance(extracted_signature_info, dict)
        else extracted_signature_info if isinstance(extracted_signature_info, str)
        else None
    )

    if extracted_signature_path:
        image = cv2.imread(extracted_signature_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            aspect_ratio = w / float(h)
            if 500 < area < 50000 and 0.2 < aspect_ratio < 5.0:
                valid_contours.append((x, y, w, h))

        if valid_contours:
            x, y, w, h = max(valid_contours, key=lambda b: b[2] * b[3])
            cropped_signature = image[y:y+h, x:x+w]
            return cropped_signature
    return None

# ✅ ORB Feature Matching for Signature Comparison
def orb_similarity(img1, img2, distance_threshold=50):
    gray1, gray2 = [
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        for img in [img1, img2]
    ]

    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)

    if des1 is None or des2 is None:
        return 0, None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(bf.match(des1, des2), key=lambda x: x.distance)

    good_matches = [m for m in matches if m.distance < distance_threshold]
    similarity = len(good_matches) / len(matches) if matches else 0
    return similarity, (kp1, kp2, good_matches, matches)

# ✅ Function to process the uploaded document image and selected reference number
def verify_signature(document_image, reference_number):
    if reference_number not in drive_links:
        return "Invalid reference number selected.", None

    # Download reference signature
    file_id = extract_file_id(drive_links[reference_number])
    reference_image_path = f"reference_signature_{reference_number}.jpg"
    download_from_drive(file_id, reference_image_path)

    # Extract signature from the document
    cropped_signature = extract_signature(document_image)
    if cropped_signature is None:
        return "Signature extraction failed.", None

    # Load reference signature
    reference_img = cv2.imread(reference_image_path)
    if reference_img is None:
        return "Error: Could not load the reference image.", None

    # Compute similarity
    similarity, details = orb_similarity(cropped_signature, reference_img)
    similarity_percentage = round(similarity * 100, 2)

    # Classification based on similarity score
    if similarity_percentage > 55:
        classification = "✅ Matched"
    elif 40 <= similarity_percentage <= 55:
        classification = "⚠️ Manual Check Recommended"
    else:
        classification = "❌ Not Matched"

    # Generate visualization of matches
    matched_img = None
    if details is not None:
        kp1, kp2, good_matches, _ = details
        matched_img = cv2.drawMatches(cropped_signature, kp1, reference_img, kp2, good_matches, None, flags=2)

    return f"🔍 Similarity Score: {similarity_percentage}%\n📌 {classification}", matched_img

# ✅ Gradio Interface
interface = gr.Interface(
    fn=verify_signature,
    inputs=[
        gr.Image(type="filepath", label="Upload Document Image"),
        gr.Number(label="Enter Reference policynumber", precision=0)
    ],
    outputs=[
        gr.Textbox(label="Verification Result"),
        gr.Image(label="Signature Matching Visualization")
    ],
    title="🖊️ Signature Verification System",
    description="Upload a document with a signature, select a policy number, and verify its authenticity.",
    theme="compact"
)

# ✅ Launch Gradio App
interface.launch(server_name="0.0.0.0", show_api=True)


