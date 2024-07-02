import os
import pandas as pd
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline 
import re
import fitz
from googletrans import Translator
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from deep_translator import GoogleTranslator
from transformers import logging
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
logging.set_verbosity_error()
# Download nltk punkt package for tokenizers
# nltk.download('punkt')
###
from .forms import UploadFileForm
import warnings
warnings.filterwarnings("ignore")


def save_uploaded_file(uploaded_file):
    form = UploadFileForm(files={'file': uploaded_file})
    if form.is_valid():
        # Save the uploaded file
        saved_file = form.save()
        return saved_file.file.url  # Return the saved file object
    else:
        # Handle the case where the form is invalid (e.g., validation errors)
        return None  

def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension


def get_content_first(x, y,doc):
    """get first  pages in document"""
    text=''
    for i in range(x,y):
        text+=' '.join(extract_text_page(doc[i]))
    return text

def answer_question_from_pdf(text, question):
    """function to define question and  return answer"""
    text_content=text.replace("\n"," ")
    # print({"text_content":text_content})
    pipe = pipeline("question-answering", model="deepset/roberta-base-squad2")
    generated_text = pipe({"question": question, "context": text_content}, max_length=100)
    return generated_text

def get_campany_name(text):
    """function to get the name of campany"""
    question="what is the company name?"
    answer=answer_question_from_pdf(text, question)
    campany_name=answer['answer'] if answer is not None else None
    return campany_name
    
def get_date_report(text):
    """function to get the date of report"""
    question="what is the year of this report?"
    answer=answer_question_from_pdf(text, question)
    campany_name=answer['answer'] if answer is not None else None
    return campany_name

def translate_text(text, language):
    """Function to translate text to be compatible with models"""
    try:
        translator = Translator()
        translated = translator.translate(text, dest=language).text
        print(translated)
        return translated
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        return None
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
        x=re.sub(r'(\w)([.!?])', r'\1 \2', x)
        sub_sentences.append(x+'.')
    return ' '.join(sub_sentences).strip()


def get_model(name, task):
    """Function to declare a model class"""
    try:
        tokenizer = AutoTokenizer.from_pretrained(name)
        model = AutoModelForSequenceClassification.from_pretrained(name)
        pipe = pipeline(task, model=model, tokenizer=tokenizer)
        return pipe
    except Exception as e:
        print(f"An error occurred while loading the model or tokenizer: {e}")
        return None
def init_models():
        """function to initialize all models to use  it """
        pipe_env=get_model("ESGBERT/EnvironmentalBERT-environmental" ,"text-classification")
        pipe_soc=get_model("ESGBERT/SocialBERT-social" ,"text-classification")
        pipe_gov=get_model("ESGBERT/GovernanceBERT-governance","text-classification")
        pipe_sent=get_model("climatebert/distilroberta-base-climate-sentiment","text-classification")
        pipe_other=get_model("distilbert-base-uncased-finetuned-sst-2-english","sentiment-analysis")
        pipe_esg= pipeline("text-classification", model="nbroad/ESG-BERT")
        return pipe_env,pipe_soc,pipe_gov,pipe_sent,pipe_other,pipe_esg
    
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

def test_sentence(sentence):
    """function to test sentence and eliminate special caracters"""
    print({"sentence": sentence})
    if sentence is not None:
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(sentence)
        if all(re.match(r'^\W+$', word) for word in words):
            return True
        if all(word.lower() in stop_words for word in words):
            return True
        if all(word.isdigit() for word in words):
            return True
        if all(re.match(r'^\W+$', word) or word.isdigit() for word in words):
            return True
        return False
    else:
        return True
def classify_sentence_label(text,pipe_env,pipe_soc,pipe_gov,pipe_esg):
    """function to classify sentence labes as E,S,G"""
    label=None
    score_class=None
    print({"tesxttt":text})
    if text is not None and pipe_env is not None and pipe_soc is not None and pipe_gov is not None and pipe_esg is not None:
        text = pipe_esg(text, padding=True, truncation=True)[0]['label']
        if text is not None:
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

def get_sentiment(label):
    if label == 'NEGATIVE':
        return 'risk'
    elif label == 'POSITIVE':
        return 'opportunity'
    else:
        return 'neutral'

def generate_recommendation(text_input):
    """function to generate recommendations based on risk detected"""
    pipe = pipeline("text-generation", model="gpt2")
    input_prompt = f"To address the risk of {text_input}, the following recommendations are suggested:\n\n "
    generated_text = pipe(input_prompt, 
        max_length=150,             
        num_return_sequences=3,     
        temperature=0.7,           
        top_p=0.9,                  
        repetition_penalty=1.2 )[0]['generated_text']
    generated_text = sent_tokenize(generated_text)
    result = "\n".join(generated_text)
    return result
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
    row['score_class']=0 if row['score_class'] is None else row['score_class']
    row['score_sentiment']=0 if row['score_sentiment'] is None else row['score_sentiment']
 
    # Calculate individual scores for each category
    if row['category']=='environmental':
        environmental_score = round((environmental_sentiment_weight * row['score_sentiment']) + (environmental_classification_weight * row['score_class']),2)
    elif row['category']=='social':
        social_score = round((social_sentiment_weight * row['score_sentiment']) + (social_classification_weight * row['score_class']),2)
    else:
        governance_score = round((governance_sentiment_weight * row['score_sentiment']) + (governance_classification_weight * row['score_class']),2)
    
    environmental_weight = 0.3
    social_weight = 0.3
    governance_weight = 0.4
    esg_score=environmental_weight*environmental_score+social_weight*social_score+governance_weight*governance_score
    return environmental_score, social_score, governance_score,esg_score

def get_total_classes(label,all_data_sentiment):
    total_label = len(all_data_sentiment[all_data_sentiment['category'] == label]) if label in all_data_sentiment['category'].values else 0
    return total_label

def get_total_sent(label,label_sent,all_data_sentiment):
    total_sent = all_data_sentiment[(all_data_sentiment['category'] == label) & (all_data_sentiment['sentiment'] == label_sent)].shape[0] if label in all_data_sentiment['category'].values else 0
    return total_sent

def calculate_total_esg(all_data_sentiment):
    """calculate total esg """
    total_e_score = round(all_data_sentiment['e_score'].sum(),2)
    total_s_score = round(all_data_sentiment['s_score'].sum(),2)
    total_g_score = round(all_data_sentiment['g_score'].sum(),2)
    ###
    environmental_weight = 0.3
    social_weight = 0.3
    governance_weight = 0.4
    esg_score=environmental_weight*total_e_score+social_weight*total_s_score+governance_weight*total_g_score
    esg_score=round(esg_score,2)
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
    
def analyse_sentence(t,pipe_env,pipe_soc,pipe_gov,pipe_esg,pipe_sent,pipe_other,sentences_class,labels_class,scores_classes,labels_sent,scores_sent):
    """function to analyse sentences and get information about each factor in the sentence"""
    t_translate=translate_text(t,"en")
    recommandation=None
    print({"t_translate":t_translate,"testtt":test_sentence(t_translate)})
    if t_translate is not None and  test_sentence(t_translate) is False:
        print({"t":t,"translate":t_translate})
        sentences_class.append(t)
        label,score_class=classify_sentence_label(t_translate,pipe_env,pipe_soc,pipe_gov,pipe_esg)
        labels_class.append(label)
        scores_classes.append(score_class)
        if label=="environmental" :
            if pipe_sent is not None:
                sentiment_env = pipe_sent([t_translate])
                sentiment_res=sentiment_env[0]['label']
                labels_sent.append(sentiment_res)
                scores_sent.append(sentiment_env[0]['score'])       
        else:
            if pipe_other is not None:
                sentiment_env = pipe_other([t_translate])
                sentiment_res=get_sentiment(sentiment_env[0]['label'])
                labels_sent.append(sentiment_res)
                scores_sent.append(sentiment_env[0]['score'])
        recommandation=generate_recommendation(t_translate) if label is not None and sentiment_res =="risk" and sentiment_env[0]['score']>=0.9  else None
        if recommandation is not None :
            print({"recommandation":recommandation})
    data={
        "factors":sentences_class,
        "category":labels_class,
        "score_class":scores_classes,
        "sentiment":labels_sent,
        "score_sentiment":scores_sent,
        "recommandation":recommandation, 
    }
    return data
   