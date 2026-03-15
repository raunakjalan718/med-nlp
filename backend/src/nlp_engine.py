import spacy
import spacy.cli
import re

class MedicalNLPEngine:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_sci_sm")
        except OSError:
            print("SciSpacy model not found. Downloading fallback web_sm model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def normalize_text(self, text):
        """
        Fixes Tesseract's 'flattening' issue by forcing line breaks 
        before known medical document anchors.
        """
        # Force a newline before major headers
        headers = [
            r'Patient Name:', r'Name:', r'Age:', r'Age/Sex:', r'Address:', 
            r'DOB:', r'Reason for Visit', r'Rx', r'Sig:', r'Additional Advice:'
        ]
        for h in headers:
            text = re.sub(rf"(?i)({h})", r"\n\1", text)
            
        # Force a newline before numbered list items (e.g., "1. ACETAMINOPHEN", "2. BENZONATATE")
        text = re.sub(r"(\s\d+\.\s+[A-Z])", r"\n\1", text)
        
        # Clean up excess whitespace
        return "\n".join([line.strip() for line in text.split('\n') if line.strip()])

    def extract_structured_data(self, raw_text):
        # 1. Normalize the messy OCR dump
        text = self.normalize_text(raw_text)

        # 2. Extract Patient Details (Flexible targeting)
        patient_name = "Not Found"
        name_match = re.search(r"(?:Patient Name|Name):\s*([A-Za-z\s\.-]+)(?:\n|Age|Date|Address|DOB|$)", text, re.IGNORECASE)
        if name_match: 
            patient_name = name_match.group(1).strip()
            
        patient_age_sex = "Not Found"
        age_match = re.search(r"(?:Age/Sex|Age):\s*([\d]+\s*[\/|\|-]?\s*[A-Za-z]+)", text, re.IGNORECASE)
        if age_match: 
            patient_age_sex = age_match.group(1).strip()

        # 3. Extract Doctor Details
        doctors = []
        doc_matches = re.finditer(r"(Dr\.?\s+[A-Za-z\s\.-]+)(?:MD|MBBS|DO|Reg|,|\n)", text, re.IGNORECASE)
        for m in doc_matches:
            clean_doc = m.group(1).strip(" -,\n")
            if len(clean_doc) > 5 and clean_doc not in doctors:
                doctors.append(clean_doc)

        # 4. Extract Medicines & Directions (State-tracking chunking)
        medicines = []
        lines = text.split('\n')
        current_med = ""

        for line in lines:
            line_lower = line.lower()
            
            # Identify the start of a new medicine (Starts with a number or contains a dosage)
            is_new_med = re.match(r"^\d+\.\s", line) or any(kw in line_lower for kw in ['mg', 'ml', 'tabs', 'caps', 'spray', 'bottle'])
            
            if is_new_med and "sig:" not in line_lower and "additional advice:" not in line_lower:
                # Save the previous medicine block before starting a new one
                if current_med: medicines.append(current_med.strip())
                current_med = line
                
            # If it's the instruction line ("Sig:"), append it to the current medicine block
            elif line_lower.startswith("sig:"):
                current_med += " \n   ↳ " + line
                
            # Catch stray lines that belong to the instructions
            elif current_med and not any(kw in line_lower for kw in ['additional advice:', 'dr.', 'reg. no']):
                current_med += " " + line

        # Don't forget to add the very last medicine tracked
        if current_med and current_med not in medicines:
            medicines.append(current_med.strip())

        # Clean up the final array to ensure we only grabbed actual drugs
        final_meds = [m for m in medicines if any(kw in m.lower() for kw in ['mg', 'ml', 'tabs', 'caps', 'spray', 'sig'])]

        return {
            "Patient_Name": patient_name if patient_name else "Not Found",
            "Patient_Age_Sex": patient_age_sex if patient_age_sex else "Not Found",
            "Doctor_Details": list(set(doctors)) if doctors else ["No doctor identified"],
            "Prescribed_Medicines": final_meds if final_meds else ["No standard dosages found"]
        }

    def process_document(self, raw_text, user_confirmed_type):
        structured_info = self.extract_structured_data(raw_text)

        return {
            "Patient_Name": structured_info["Patient_Name"],
            "Patient_Age_Sex": structured_info["Patient_Age_Sex"],
            "Doctor_Details": structured_info["Doctor_Details"],
            "Prescribed_Medicines": structured_info["Prescribed_Medicines"]
        }