import os
import PyPDF2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation 
from sklearn.cluster import KMeans
from transformers import BertTokenizer, BertModel
import torch

def get_pdf_text(pdf_path):
    """
    Extract the text from a PDF file.
    """
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    return text


def summarize_pdf(pdf_text, n_topics=3, n_sentences=3, max_seq_length=512):
    """
    Summarize the content of a PDF file using a machine learning algorithm.
    """
    # Split the input text into smaller chunks
    chunks = [pdf_text[i:i+max_seq_length] for i in range(0, len(pdf_text), max_seq_length)]

    # Process each chunk and combine the resulting summaries
    summary = ''
    for chunk in chunks:
        # Convert the text to a TF-IDF matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform([chunk])

        # Use Latent Dirichlet Allocation (LDA) to identify topics
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        document_topics = lda.fit_transform(tfidf_matrix)

        # Use BERT to embed the sentences
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertModel.from_pretrained('bert-base-uncased')
        sentence_embeddings = []
        sentences = chunk.split('.')
        if len(sentences) < n_topics:
            n_topics = len(sentences)
        for sentence in sentences:
            input_ids = torch.tensor([tokenizer.encode(sentence, add_special_tokens=True)])
            with torch.no_grad():
                last_hidden_state = model(input_ids)[0]
            sentence_embeddings.append(last_hidden_state.mean(dim=1).squeeze().numpy())

        # Cluster the sentences using K-Means
        kmeans = KMeans(n_clusters=n_topics, random_state=42)
        sentence_clusters = kmeans.fit_predict(sentence_embeddings)

        # Identify the most important sentences for each topic
        chunk_summary = ''
        for topic_idx in range(n_topics):
            important_sentence_indices = np.where(sentence_clusters == topic_idx)[0][-n_sentences:]
            important_sentences = [sentences[i] for i in important_sentence_indices]
            chunk_summary += '. '.join(important_sentences) + '. '

        summary += chunk_summary.strip() + ' '

    return summary.strip()
# Example usage
pdf_path = r'D:\IA\sustex-coporate\esganalyse\test.pdf'
pdf_text = get_pdf_text(pdf_path)
summary = summarize_pdf(pdf_text)
print(summary)