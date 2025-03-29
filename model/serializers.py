from rest_framework import serializers
from .models import InsuranceData

class InsuranceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceData
        fields = '__all__'  # Include all fields

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()