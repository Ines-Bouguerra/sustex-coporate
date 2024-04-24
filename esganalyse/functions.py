import pandas as pd
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline 
import re
import fitz
from googletrans import Translator
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
# Download nltk punkt package for tokenizers
# nltk.download('punkt')
###
from django.core.files.storage import FileSystemStorage

def save_uploaded_file(uploaded_file):
    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)
    return fs.path(filename)


def translate_text(text,language):
    """function to translate text to be compatible with models"""
    translator = Translator()
    translated = translator.translate(text, src='auto', dest=language)
    return translated.text

##
def extract_from_pdf(path):
    """function extract_from_pdf """
    doc = fitz.open(path)
    return doc

def extract_text_page(page):
    """function extract_text_page each page with their contents"""
    text = page.get_text("text")
    text=text.split('\n')
    text=[x.strip() for x in text if x.strip()!=""]
    return text 
    
def list_to_string(title_contenu):
    """function to deal with dict data to convert it to str"""
    sub_sentences=[]
    for x in title_contenu:
        x=x.replace('\n',' ')
        x=re.sub(r'(\w)([.,!?])', r'\1 \2', x)
        sub_sentences.append(x+'.')
    return ' '.join(sub_sentences).strip()

def get_model(name,task):
    """function to declare a model class"""
    # In simple words, the tokenizer prepares the text for the model and the model classifies the text-
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name)
    # The pipeline combines tokenizer and model to one process.
    pipe= pipeline(task, model=model, tokenizer=tokenizer)
    return pipe

def proprocess_text_data(multi_lang_text):
    """function to preprocess data from pdf"""
    sentences = nltk.tokenize.sent_tokenize(multi_lang_text)
    complete_sentences = []
    current_sentence = ""
    for sentence in sentences:
        current_sentence += sentence.strip() + " "
        if sentence.endswith(('.', '!', '?',':')):
            complete_sentences.append(current_sentence.strip())
            current_sentence = ""

    if current_sentence:
        complete_sentences.append(current_sentence.strip())
    return complete_sentences

def get_word_entity(text):
    """function to use NER algorithm to GET word entities"""
    all_entities=[]
    for x in text:
        ner_tagger = pipeline("ner", aggregation_strategy="simple", 
                        model="dbmdz/bert-large-cased-finetuned-conll03-english")
        outputs = ner_tagger(x)
    all_entities+=outputs
    return all_entities

def get_campany_name(output):
    """function to use NER algorithm to GET word entities"""
    org_entities = [entity['word'] for entity in output if entity['entity_group'] == 'ORG']
    most_common_word = max(set(org_entities), key=org_entities.count)
    return most_common_word

def classify_sentence_label(text,pipe_env,pipe_soc,pipe_gov):
    """function to classify sentence labes as E,S,G"""
    env = pipe_env(text, padding=True, truncation=True)
    if env[0]['label']!='none':
        label=env[0]['label']
        score_class=env[0]['score']
    else:
        social=pipe_soc(text, padding=True, truncation=True)
        if social[0]['label']!='none':
            label=social[0]['label']
            score_class=social[0]['score']
            
        else:
            gov=pipe_gov(text, padding=True, truncation=True)
            if gov[0]['label']!='none':
                label=gov[0]['label']
                score_class=gov[0]['score']
    return label,score_class

def get_sentiment(score):
    if score >= 0.6:
        return 'opportunity'
    elif score <= 0.4:
        return 'risk'
    else:
        return 'neutral'

# Define the calculate_esg_scores function
def calculate_esg_scores(row):
    """
    Calculate the individual Environmental (E), Social (S), and Governance (G) scores 
    based on sentiment and classification scores.
    """
    
    # Assign weights to sentiment and classification scores for each category
    environmental_sentiment_weight = 0.3
    environmental_classification_weight = 0.7
    social_sentiment_weight = 0.3
    social_classification_weight = 0.7
    governance_sentiment_weight = 0.3
    governance_classification_weight = 0.7
    ####
    environmental_score=0
    ##
    social_score=0
    ##
    governance_score=0
    # Calculate individual scores for each category
    if row['category']=='environmental':
        environmental_score = round((environmental_sentiment_weight * row['score_sentiment']) + (environmental_classification_weight * row['score_class']),2)
    elif row['category']=='social':
        social_score = round((social_sentiment_weight * row['score_sentiment']) + (social_classification_weight * row['score_class']),2)
    else:
        governance_score = round((governance_sentiment_weight * row['score_sentiment']) + (governance_classification_weight * row['score_class']),2)
    return environmental_score, social_score, governance_score

def get_total_classes(label,all_data_sentiment):
    total_label = all_data_sentiment[all_data_sentiment['category'] == label].shape[0]
    return total_label

def get_total_sent(label,label_sent,all_data_sentiment):
    total_sent = all_data_sentiment[(all_data_sentiment['category'] == label) & (all_data_sentiment['sentiment'] == label_sent)].shape[0]
    return total_sent

def calculate_total_esg(all_data_sentiment):
    """calculate total esg """
    total_e_score = all_data_sentiment['e_score'].sum()
    total_s_score = all_data_sentiment['s_score'].sum()
    total_g_score = all_data_sentiment['g_score'].sum()
    ###
    environmental_weight = 0.3
    social_weight = 0.3
    governance_weight = 0.4
    esg_score=environmental_weight*total_e_score+social_weight*total_s_score+governance_weight*total_g_score
    return esg_score,total_e_score,total_s_score,total_g_score

def get_classes(all_data_sentiment):
    total_environmental_label = get_total_classes("environmental",all_data_sentiment)
    total_social_label = get_total_classes("social",all_data_sentiment)
    total_governance_label = get_total_classes("governance",all_data_sentiment)
    return total_environmental_label, total_social_label,total_governance_label


def get_sent_env(all_data_sentiment):
    total_environmental_neutral =  get_total_sent('environmental',"neutral",all_data_sentiment)
    total_environmental_risk = get_total_sent('environmental',"risk",all_data_sentiment)
    total_environmental_opportunity = get_total_sent('environmental',"opportunity",all_data_sentiment)
    return total_environmental_neutral,total_environmental_risk,total_environmental_opportunity

def get_sent_soc(all_data_sentiment):
    total_social_neutral =  get_total_sent('social',"neutral",all_data_sentiment)
    total_social_risk = get_total_sent('social',"risk",all_data_sentiment)
    total_social_opportunity = get_total_sent('social',"opportunity",all_data_sentiment)
    return total_social_neutral,total_social_risk,total_social_opportunity
    
def get_sent_gov(all_data_sentiment):
    total_governance_neutral =  get_total_sent('governance',"neutral",all_data_sentiment)
    total_governance_risk = get_total_sent('governance',"risk",all_data_sentiment)
    total_governance_opportunity = get_total_sent('governance',"opportunity",all_data_sentiment)
    return total_governance_neutral,total_governance_risk,total_governance_opportunity   
    
