import spacy
import fitz
# Load the pre-trained English NER model
from transformers import pipeline
# Function to answer questions based on the context
def answer_question(question,context):
    model="Ayushb/roberta-base-ft-esg"
    qa_pipeline = pipeline("question-answering", model=model, tokenizer=model)
    
    answer = qa_pipeline(question=question, context=context)
    return answer

# questions = [
#     # "What are the key environmental metrics reported by the company?",
#     # "Are there any anomalies in the reported employee turnover rates?",
#     # "How does the company's governance score compare to industry benchmarks?"
#     "What are the company's carbon emission targets?",
#     "How does the company handle waste management?"
# ]
questions = [
    "Quels sont les objectifs de réduction des émissions de carbone de l'entreprise pour les cinq prochaines années ?",
    "Pouvez-vous fournir des détails sur les initiatives de l'entreprise visant à réduire la génération de déchets et à augmenter les taux de recyclage ?",
    "Pourriez-vous énumérer les principaux indicateurs de performance environnementale suivis et rapportés par l'entreprise ?",
    "Y a-t-il eu des écarts significatifs dans les taux de rotation du personnel par rapport aux moyennes de l'industrie ou aux tendances historiques ?",
    "Comment la notation de gouvernance de l'entreprise dans les évaluations ESG se compare-t-elle aux pairs du secteur ou aux normes de l'industrie ?"
]

def extract_text_from_pdf(pdf_path,questions):
    doc = fitz.open(pdf_path)
    # text = ''
    for i in range(0,len(doc)):
        text = doc[i].get_text("text")
        text=text.replace('\n'," ")
        for question in questions:
            answer=answer_question(question,text)
            print({"question": question, "answer": answer})
    # return text

path = r"D:\IA\sustex-coporate\media\uploads\orange_rapport-annuel-integre-2022_7mgPTTo.pdf"
extract_text_from_pdf(path,questions)

