import spacy

class MedicalNLPEngine:
    def __init__(self):
        # Load the SciSpacy medical NER model
        try:
            self.nlp = spacy.load("en_core_sci_sm")
        except OSError:
            raise OSError("Please install the en_core_sci_sm model first.")

        # Simple keyword sets for text-based classification
        self.prescription_keywords = {'rx', 'po', 'bid', 'mg', 'tablet', 'pharmacy', 'refill', 'sig'}
        self.lab_keywords = {'range', 'g/dl', 'specimen', 'hemoglobin', 'assay', 'plasma', 'serum'}

    def classify_text(self, text):
        """Classify document type based on NLP vocabulary matching."""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        rx_score = len(words.intersection(self.prescription_keywords))
        lab_score = len(words.intersection(self.lab_keywords))
        
        if rx_score > lab_score:
            return "Prescription"
        elif lab_score > rx_score:
            return "Lab Report"
        else:
            return "Clinical Note / Unclassified"

    def extract_entities(self, text):
        """Run SciSpacy NER to pull out medical entities."""
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            # SciSpacy recognizes entities like diseases, drugs, and body parts
            entities.append({
                "text": ent.text,
                "label": ent.label_ # Usually 'ENTITY' in the basic sci model, but captures medical terms
            })
        return entities

    def process_document(self, raw_text):
        """The main pipeline for structuring the text."""
        doc_type = self.classify_text(raw_text)
        extracted_data = self.extract_entities(raw_text)
        
        # Return structured JSON-ready dictionary
        return {
            "document_type": doc_type,
            "raw_text_length": len(raw_text),
            "medical_entities_found": len(extracted_data),
            "extracted_entities": extracted_data
        }