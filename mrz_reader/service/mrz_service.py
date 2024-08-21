from injector import inject
import logging
from mrz.checker.td1 import TD1CodeChecker
from mrz.checker.td2 import TD2CodeChecker
from mrz.checker.td3 import TD3CodeChecker
logger = logging.getLogger("ocr-ids-be")


class MrzService:

    @inject
    def __init__(self):
        logger.info("MrzService instance created")
    
    def extractTD1(self, mrz):
        td1_check = TD1CodeChecker(mrz)
        fields = td1_check.fields()

        return fields
    
    def extractTD2(self, mrz):
        td1_check = TD2CodeChecker(mrz)
        fields = td1_check.fields()

        return fields
    
    def extractTD3(self, mrz):
        td1_check = TD3CodeChecker(mrz)
        fields = td1_check.fields()

        return fields
        
