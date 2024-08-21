import logging

logger = logging.getLogger("ocr-ids-be")

class OcrDataConverter():

    @staticmethod
    def paddle_result_to_mrz(result):
        mrz = ""
        for text in result:
            text_len = len(text)
            if "<" in text:
                text.replace(" ", "<")
                if text_len == 44:
                    mrz = mrz + text + "\n"
                elif text_len < 44:
                    need_len = 44 - text_len
                    mrz = mrz + text + ("<" * need_len) + "\n"
                elif text_len > 44:
                    need_len = text_len - 44
                    for _ in range(need_len):
                        text = text.replace("<", "", 1)
                    mrz = mrz + text + "\n"

        mrz = mrz.rstrip('\n').upper()

        return mrz
    
    @staticmethod
    def paddle_result_to_sim(result):
        sim = []
        temp_text = ""
        for text in result:
            logger.info(f"text :  {text}")
            if 'SURAT IZIN MENGEMUDI' in temp_text.upper():
                sim.append(text.upper().strip())
            elif len(sim) >= 1:
                sim.append(text)
            temp_text = text
        
        return sim