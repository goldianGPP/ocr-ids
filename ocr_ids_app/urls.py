from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .controller.ocr_ids_controller import OcrIdsController

router = DefaultRouter()
router.register(r'v1/ocr', OcrIdsController, basename='ocr-ids')

urlpatterns = [
    path('', include(router.urls)),
]
