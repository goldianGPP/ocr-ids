import re
from thefuzz import fuzz
from datetime import datetime

class OcrResultConverter():

    @staticmethod
    def to_passport_response_dto(mrz_result):
        passportResponseDto = {}
        passportResponseDto['documentNumber'] = mrz_result.document_number
        passportResponseDto['name'] = mrz_result.name
        passportResponseDto['surname'] = mrz_result.surname
        
        try:
            passportResponseDto['birthDate'] = OcrResultConverter._convert_date(mrz_result.birth_date)
        except Exception as e:
            passportResponseDto['birthDate'] = None

        try:
            passportResponseDto['expiryDate'] = OcrResultConverter._convert_date(mrz_result.expiry_date)
        except Exception as e:
            passportResponseDto['expiryDate'] = None

        passportResponseDto['gender'] = mrz_result.sex
        passportResponseDto['nationality'] = mrz_result.nationality
        passportResponseDto['country'] = mrz_result.country
        passportResponseDto['optionalData'] = mrz_result.optional_data


        hashes = {}
        hashes['birthDateHash'] = mrz_result.birth_date_hash
        hashes['expiryDateHash'] = mrz_result.expiry_date_hash
        hashes['documentNumberHash'] = mrz_result.document_number_hash
        hashes['optionalDataHash'] = mrz_result.optional_data_hash
        hashes['finalHash'] = mrz_result.optional_data_hash

        passportResponseDto['hashes'] = hashes

        return passportResponseDto
    
    @staticmethod
    def to_ktp_response_dto(result):
        ktpResponseDto = {}

        thereshold = 90
        
        def get_most_similar_part(key, text, threshold=thereshold):
            # Split the text into possible parts by spaces
            parts = text.split()
            best_match = ""
            highest_ratio = 0

            # Check similarity of each part with the key
            for part in parts:
                ratio = fuzz.partial_ratio(key.upper(), part.upper())
                if ratio > highest_ratio and ratio >= threshold:
                    highest_ratio = ratio
                    best_match = part

            return best_match, highest_ratio

        for text in result:
            if 'NIK' in text.upper() or (similar := get_most_similar_part('NIK', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'NIK'
                ktpResponseDto["nik"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'NAMA' in text.upper() or (similar := get_most_similar_part('NAMA', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'NAMA'
                ktpResponseDto["fullName"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'TEMPAT/TGL LAHIR' in text.upper() or (similar := get_most_similar_part('TEMPAT/TGL LAHIR', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'TEMPAT/TGL LAHIR'
                ktpResponseDto["birthDate"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'JENIS KELAMIN' in text.upper() or (similar := get_most_similar_part('JENIS KELAMIN', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'JENIS KELAMIN'
                text_result = text.upper().replace(found_part, "").replace(" : ", ":").replace(": ", ":").replace(" :", ":").replace(":", ": ")

                if 'GOL. DARAH' in text_result.upper() or (similar_2 := get_most_similar_part('GOL. DARAH', text_result))[1] >= thereshold:
                    found_part_2 = similar_2[0] if similar_2[1] >= thereshold else 'GOL. DARAH'
                    text_result_2 = text_result.upper().replace(found_part_2, "").replace(":", "").strip()
                    text_result_2_split = text_result_2.split(" ")
                    ktpResponseDto["gender"] = text_result_2_split[0]
                    for i in range(1, len(text_result_2_split)):
                        bloodType = text_result_2_split[i]
                        if bool(bloodType.strip()):
                            ktpResponseDto["bloodType"] = bloodType
                else:
                    ktpResponseDto["gender"] = text_result.replace(":", "").strip()

            elif 'ALAMAT' in text.upper() or (similar := get_most_similar_part('ALAMAT', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'ALAMAT'
                ktpResponseDto["address"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'RT/RW' in text.upper() or (similar := get_most_similar_part('RT/RW', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'RT/RW'
                ktpResponseDto["address"] = f"{ktpResponseDto.get('address', '')}, {text.upper().replace(found_part, '').replace(':','').strip()}"

            elif 'KEL/DESA' in text.upper() or (similar := get_most_similar_part('KEL/DESA', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'KEL/DESA'
                ktpResponseDto["address"] = f"{ktpResponseDto.get('address', '')}, {text.upper().replace(found_part, '').replace(':','').strip()}"

            elif 'KECAMATAN' in text.upper() or (similar := get_most_similar_part('KECAMATAN', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'KECAMATAN'
                ktpResponseDto["address"] = f"{ktpResponseDto.get('address', '')}, {text.upper().replace(found_part, '').replace(':','').strip()}"

            elif 'AGAMA' in text.upper() or (similar := get_most_similar_part('AGAMA', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'AGAMA'
                ktpResponseDto["religion"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'STATUS PERKAWINAN' in text.upper() or (similar := get_most_similar_part('STATUS PERKAWINAN', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'STATUS PERKAWINAN'
                ktpResponseDto["maritalStatus"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'PEKERJAAN' in text.upper() or (similar := get_most_similar_part('PEKERJAAN', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'PEKERJAAN'
                ktpResponseDto["designation"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'KEWARGANEGARAAN' in text.upper() or (similar := get_most_similar_part('KEWARGANEGARAAN', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'KEWARGANEGARAAN'
                ktpResponseDto["nationalityStatus"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif 'BERLAKU HINGGA' in text.upper() or (similar := get_most_similar_part('BERLAKU HINGGA', text))[1] >= thereshold:
                found_part = similar[0] if similar[1] >= thereshold else 'BERLAKU HINGGA'
                ktpResponseDto["expiryDate"] = text.upper().replace(found_part, "").replace(":", "").strip()

            elif re.match(r'^\d{2}-\d{2}-\d{4}$', text.strip()):
                ktpResponseDto["issuedDate"] = text.strip()

        return ktpResponseDto
    
    @staticmethod
    def to_sim_response_dto(sim_result):
        simResponseDto = {}
        simResponseDto["documentType"] = sim_result[0]
        simResponseDto["documentNumber"] = sim_result[1]
        simResponseDto["fullName"] = sim_result[2].replace("1. ", "")

        place_date_birth = sim_result[3].replace("2. ", "").split(",")
        simResponseDto["birthPlace"] = place_date_birth[0].strip()
        simResponseDto["birthDate"] = place_date_birth[1].strip()

        blood_gender = sim_result[4].replace("3. ", "").split("-")
        simResponseDto["bloodType"] = blood_gender[0]
        simResponseDto["gender"] = blood_gender[1]

        simResponseDto["address"] = (f"{sim_result[5].replace('4. ', '')}, {sim_result[6]}, {sim_result[7]}, {sim_result[9].replace('6. ', '')}").replace(", ", ",").replace(",", ", ")
        simResponseDto["status"] = sim_result[8]
        simResponseDto["expiryDate"] = sim_result[10]

        return simResponseDto


    @staticmethod
    def _convert_date(input_date):
        input_date = str(input_date)
        date_object = datetime.strptime(input_date, '%y%m%d')
        formatted_date = date_object.strftime('%d-%m-%Y')

        return formatted_date
