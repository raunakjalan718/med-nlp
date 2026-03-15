import spacy
import spacy.cli

class MedicalNLPEngine:
    def __init__(self):
        try:
            # Loads the specialized medical model
            self.nlp = spacy.load("en_core_sci_sm")
        except OSError:
            print("SciSpacy model not found. Downloading fallback web_sm model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            
        self.rx_words = {'rx', 'po', 'bid', 'mg', 'tablet', 'pharmacy', 'refill', 'sig', 'dose', 'medication'}
        self.lab_words = {'range', 'g/dl', 'specimen', 'hemoglobin', 'assay', 'plasma', 'serum', 'test'}

    def classify_text(self, text):
        words = set(text.lower().split())
        rx_score = len(words.intersection(self.rx_words))
        lab_score = len(words.intersection(self.lab_words))
        
        if rx_score > lab_score: return "Prescription"
        if lab_score > rx_score: return "Lab Report"
        return "Clinical Note"

    def process_document(self, raw_text, user_confirmed_type):
        doc_type = self.classify_text(raw_text)
        doc = self.nlp(raw_text)
        medical_terms = list(set([ent.text for ent in doc.ents]))

        return {
            "Document_Type": doc_type,
            "User_Confirmation": user_confirmed_type,
            "Total_Characters_Read": len(raw_text),
            "Extracted_Medical_Entities": medical_terms[:20], # Capped for clean UI
            "Raw_Text_Preview": raw_text[:250] + "..."
        }