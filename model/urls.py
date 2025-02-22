from django.urls import path
from .views import predict_json, predict_file

urlpatterns = [
     path("predict/", predict_json, name="predict_json"),
     path('predict_file/', predict_file, name="predict_file")
]