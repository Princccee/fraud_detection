import tensorflow as tf
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .serializers import InsuranceDataSerializer
from .utils import preprocess_input
import os
import numpy as np

# Load model once when Django starts
model_path = os.path.join(os.path.dirname(__file__), "model.h5")
model = tf.keras.models.load_model(model_path)


@api_view(["POST"])
def predict(request):
    serializer = InsuranceDataSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data

        processed_input = preprocess_input(data) # pre-process the imput recived
        
        prediction = model.predict([processed_input])  # Adjust based on your model's input shape
        fraud_probability = float(prediction[0][0])

        return JsonResponse({"fraud_probability": fraud_probability})
    
    return JsonResponse(serializer.errors, status=400)
