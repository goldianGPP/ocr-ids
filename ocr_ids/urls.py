from django.urls import path, include

urlpatterns = [
    path('api/', include('ocr_ids_app.urls')),
]