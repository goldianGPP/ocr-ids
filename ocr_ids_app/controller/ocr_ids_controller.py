from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from injector import inject
from ..service.ocr_ids_service import OcrIdsService

class OcrIdsController(viewsets.ViewSet):

    @inject
    def __init__(self, ocrIdsService: OcrIdsService, *args, **kwargs):
        self.ocrIdsService = ocrIdsService
        super().__init__(*args, **kwargs)

    @action(detail=False, methods=['post'], url_path='passport')
    def extract_passport(self, request, *args, **kwargs):
        request_body = request.data
        result = self.ocrIdsService.extract_passport(request_body.get("image"))

        if result:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"error": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='ktp')
    def extract_ktp(self, request, *args, **kwargs):
        request_body = request.data
        result = self.ocrIdsService.extract_ktp(request_body.get("image"))

        if result:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"error": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='sim')
    def extract_sim(self, request, *args, **kwargs):
        request_body = request.data
        result = self.ocrIdsService.extract_sim(request_body.get("image"))

        if result:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"error": "failed"}, status=status.HTTP_400_BAD_REQUEST)
