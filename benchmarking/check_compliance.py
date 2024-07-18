import spacy
from PyPDF2 import PdfReader

# Charger un modèle de langue pour l'analyse textuelle
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file):
    print("Extracting text from PDF...")

    text = ""
    pdf_reader = PdfReader(file)
    
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def parse_criteria_from_text(text):
    criteria = {}
    lines = text.split('\n')
    current_key = None
    
    for line in lines:
        if line.strip():
            if ':' in line:
                key, value = line.split(':', 1)
                current_key = key.strip()
                criteria[current_key] = [term.strip() for term in value.split(',')]
            elif current_key:
                # This line is a continuation of the previous key's values
                criteria[current_key].extend([term.strip() for term in line.split(',')])
    
    return criteria

def check_compliance(document_text, criteria):
    doc = nlp(document_text)
    compliance_results = {key: False for key in criteria}
    
    for key, terms in criteria.items():
        for sentence in doc.sents:
            if any(term in sentence.text.lower() for term in terms):
                compliance_results[key] = True
                break
    
    return compliance_results