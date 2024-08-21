from injector import inject
from ocr_paddleocr.service.extract_text_service import ExtractTextService
from mrz_reader.service.mrz_service import MrzService
from ..converter.ocr_data_converter import OcrDataConverter
from ..converter.ocr_result_converter import OcrResultConverter
import logging
from ocr_ids.exceptions import BusinessException
import time

logger = logging.getLogger("ocr-ids-be")


class OcrIdsService:

    @inject
    def __init__(self, extractTextService: ExtractTextService, mrzService: MrzService):
        self.extractTextService = extractTextService
        self.mrzService = mrzService
        logger.info("OcrIdsService instance created")

    def extract_passport(self, base64_image):
        start_time = time.time()
        logger.info(f"Initial time: {start_time - start_time} seconds")

        result = self.extractTextService.extract_from_base64(base64_image)
        after_extraction_time = time.time()
        logger.info(f"After extraction: {after_extraction_time - start_time} seconds")

        mrz = OcrDataConverter.paddle_result_to_mrz(result)
        logger.info("\n")
        logger.info(f"MRZ string: {mrz}")

        try:
            mrz_result = self.mrzService.extractTD3(mrz)
            after_formation_time = time.time()
            logger.info(f"After formation: {after_formation_time - after_extraction_time} seconds")
            
            passportResponseDto = OcrResultConverter.to_passport_response_dto(mrz_result)
            after_conversion_time = time.time()
            logger.info(f"After conversion: {after_conversion_time - after_formation_time} seconds")
            
            return passportResponseDto
        except Exception as e:
            raise BusinessException("MRZ Data not found", "MRZ-00003")
        
    def extract_ktp(self, base64_image):
        start_time = time.time()
        logger.info(f"Initial time: {start_time - start_time} seconds")

        result = self.extractTextService.extract_from_base64(base64_image, distance_threshold=90)
        after_extraction_time = time.time()
        logger.info(f"After extraction: {after_extraction_time - start_time} seconds")

        try:
            simResponseDto = OcrResultConverter.to_ktp_response_dto(result)
            after_conversion_time = time.time()
            logger.info(f"After conversion: {after_conversion_time - after_extraction_time} seconds")
            
            return simResponseDto
        except Exception as e:
            raise BusinessException("MRZ Data not found", "MRZ-00003")
        
    def extract_sim(self, base64_image):
        start_time = time.time()
        logger.info(f"Initial time: {start_time - start_time} seconds")

        result = self.extractTextService.extract_from_base64(base64_image, distance_threshold=60, w_threshold=False)
        after_extraction_time = time.time()
        logger.info(f"After extraction: {after_extraction_time - start_time} seconds")

        sim = OcrDataConverter.paddle_result_to_sim(result)
        logger.info("\n")
        logger.info(f"SIM array: {sim}")

        try:
            simResponseDto = OcrResultConverter.to_sim_response_dto(sim)
            after_conversion_time = time.time()
            logger.info(f"After conversion: {after_conversion_time - after_extraction_time} seconds")
            
            return simResponseDto
        except Exception as e:
            raise BusinessException("MRZ Data not found", "MRZ-00003")
