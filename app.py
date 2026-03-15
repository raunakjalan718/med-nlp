import json
import os
from src.gatekeeper import DocumentGatekeeper
from src.ocr_bridge import extract_raw_text
from src.nlp_engine import MedicalNLPEngine

def main():
    print("Initializing Models... (This might take a few seconds)")
    gatekeeper = DocumentGatekeeper()
    nlp_engine = MedicalNLPEngine()
    
    # Target a test file in your data folder
    test_file = "data/sample_prescription.jpg" 
    
    if not os.path.exists(test_file):
        print(f"Please add a test image to {test_file} to run the pipeline.")
        return

    print(f"\nProcessing file: {test_file}")
    
    # 1. Visual Routing
    category = gatekeeper.route_document(test_file)
    print(f"Gatekeeper Classification: {category}")
    
    if category == "SCAN":
        print("Action: File is an X-Ray/MRI. Routing to Visual Storage Bucket.")
        # Stop here, no NLP needed for visual scans
        structured_output = {"status": "Stored as Medical Scan", "file": test_file}
        
    elif category == "DOCUMENT":
        print("Action: File is a text document. Initiating NLP Pipeline...")
        
        # 2. Extract Text
        raw_text = extract_raw_text(test_file)
        
        if "OCR Error" in raw_text or len(raw_text) < 5:
            print("Failed to extract meaningful text.")
            return
            
        # 3. NLP Structuring
        structured_data = nlp_engine.process_document(raw_text)
        
        structured_output = {
            "status": "Processed via NLP",
            "file": test_file,
            "data": structured_data
        }
        
    # Output the final structural JSON
    print("\n--- FINAL STRUCTURED JSON OUTPUT ---")
    print(json.dumps(structured_output, indent=4))

if __name__ == "__main__":
    main()