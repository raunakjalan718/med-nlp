import spacy
import spacy.cli
import re

class TextSanitizer:
    """Fixes Tesseract's layout errors before extraction begins."""
    @staticmethod
    def clean(raw_text):
        # 1. Remove OCR 'noise' like phantom margin numbers (1), (2)
        text = re.sub(r'^\(\d+\)\s*', '', raw_text, flags=re.MULTILINE)
        
        # 2. Inject line breaks before known headers to prevent 'paragraph-lumping'
        headers = ['Patient Name:', 'Age:', 'Address:', 'DOB:', 'Rx', 'Sig:', 'Additional Advice:']
        for h in headers:
            text = re.sub(rf"(?i)({h})", r"\n\1", text)
        
        # 3. Standardize numbering
        text = re.sub(r"(\d+\.\s+)", r"\n\1", text)
        
        return "\n".join([line.strip() for line in text.split('\n') if line.strip()])

class PrescriptionParser:
    """Extracts specific clinical information using structural anchors."""
    def __init__(self, text):
        self.text = text

    def get_patient(self):
        name, age_sex = "Not Found", "Not Found"
        # Anchor: Between 'Name' and next common field
        n_match = re.search(r"(?:Patient Name|Name)[\s:]+(.*?)(?:\s+Age|\s+Date|\s+Address|\n|$)", self.text, re.IGNORECASE)
        if n_match: name = n_match.group(1).strip(" .,-")
        
        a_match = re.search(r"(?:Age/Sex|Age)[\s:]*([\d]+[\s/|-]*[A-Za-z]*)", self.text, re.IGNORECASE)
        if a_match: age_sex = a_match.group(1).strip()
        return name, age_sex

    def get_doctors(self):
        doctors = []
        # Exclude common address keywords to avoid 'Oak Street' showing up as a doctor
        exclude = {'Street', 'Plaza', 'Avenue', 'Road', 'Hospital', 'Clinic', 'Healthville'}
        
        matches = re.finditer(r"(?:Dr\.?\s+([A-Za-z\s\.-]+?)(?:,|$|\n|Reg))|([A-Za-z\s\.-]+?)(?:,\s*(?:M\.D\.|MBBS|DO))", self.text, re.IGNORECASE)
        for m in matches:
            name = (m.group(1) or m.group(2)).strip().title()
            if len(name) > 3 and not any(word in name for word in exclude):
                doctors.append(name)
        return list(set(doctors)) if doctors else ["No doctor identified"]

    def get_meds(self):
        # Isolate the Rx zone
        rx_zone = re.split(r"(?i)Additional Advice|Refill|Label|Generic|Dispense", self.text)[0]
        rx_match = re.search(r"(?is)(?:Rx|R\s|Diagnosis.*?)(.*)", rx_zone)
        zone = rx_match.group(1) if rx_match else self.text
        
        meds = []
        # Path A: Check for numbered list (Case for current image)
        if any(re.match(r"^\d+\.", line) for line in zone.split('\n')):
            blocks = re.split(r"(?m)^\d+\.\s", zone)
            for b in blocks:
                if len(b.strip()) > 5:
                    # Clean the block: Drug on top, Sig nested
                    item = re.sub(r'\s*Sig:', '\n  ↳ Sig:', b.strip(), flags=re.IGNORECASE)
                    meds.append(item)
        # Path B: Standard block parsing
        else:
            current = []
            for line in zone.split('\n'):
                current.append(line)
                if line.lower().startswith('sig:'):
                    meds.append("\n  ↳ ".join([" ".join(current[:-1]), current[-1]]))
                    current = []
        return [m.strip() for m in meds if len(m) > 5]

class MedicalNLPEngine:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_sci_sm")
        except OSError:
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def process_document(self, raw_text, user_confirmed_type):
        clean_text = TextSanitizer.clean(raw_text)
        parser = PrescriptionParser(clean_text)
        
        name, age_sex = parser.get_patient()
        
        return {
            "Patient_Name": name,
            "Patient_Age_Sex": age_sex,
            "Doctor_Details": parser.get_doctors(),
            "Prescribed_Medicines": parser.get_meds()
        }