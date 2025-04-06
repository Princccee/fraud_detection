from django.urls import path
from .views import predict_json, predict_file, download_file, verify_signature

urlpatterns = [
     path("predict/", predict_json, name="predict_json"),
     path('predict_file/', predict_file, name="predict_file"),
     path('download_file/', download_file, name="download_file"),
     path('frogery_test/', verify_signature, name="frogery_test"),
]