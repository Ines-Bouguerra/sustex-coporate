import asyncio
import logging
import json
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .serializers import CampanySerializer,CampanyDetailsSerializer
from django.db.models import Q
from esganalyse.functions import extract_from_pdf,extract_text_page,list_to_string,proprocess_text_data,get_model,classify_sentence_label,get_sentiment,get_word_entity,get_campany_name,calculate_total_esg,calculate_esg_scores,get_classes,get_sent_env,get_sent_soc,get_sent_gov, save_uploaded_file
import os
logger = logging.getLogger(__name__) 
class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info('WebSocket connection established')
        await self.accept()
        await self.channel_layer.group_add(
            "chart_group_global",
            self.channel_name,
        )
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        year = text_data_json['id']
        campany_name=text_data_json['password']
        file_path = text_data_json.get('file_path')
        
        if file_path and os.path.exists(file_path):
            saved_file_path = save_uploaded_file(file_path)
            asyncio.create_task(self.start_data_loop_global_chart(campany_name,year,saved_file_path))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
    
    ##function to save in database asynchrononsly
    @database_sync_to_async
    def save_system_usage(self, all_data_sentiment,document_data):
        if not CampanySerializer.objects.filter(Q(campany_name=document_data['campany_name'])& Q (year=document_data['year'])).exists():
            # Create a serializer instance
            dashboard_serializer = CampanySerializer(data=document_data)
        else:
            object_serializer=CampanySerializer.objects.get(Q(campany_name=document_data['campany_name'])& Q (year=document_data['year']))
            dashboard_serializer = CampanySerializer(object_serializer,data=document_data)
        # Check if the data is valid
        if dashboard_serializer.is_valid():
            dashboard_instance = dashboard_serializer.save()
            id_campany = dashboard_instance.id
            if id_campany is not None:
                for sentence in all_data_sentiment:
                    sentence['campany']=id_campany
                    sentence_serializer = CampanyDetailsSerializer(data=sentence)
                    if sentence_serializer.is_valid():
                        # Save the new data
                        sentence_serializer.save()

       
    async def start_data_loop_global_chart(self,campany_name,year,path):
        # path="../resources/orange_rapport-annuel-integre-2022.pdf"
        doc= extract_from_pdf(path)
        sentences_class=[]
        labels_class=[]
        scores_classes=[]
        labels_sent=[]
        scores_sent=[]
        for page in doc:
            text=extract_text_page(page)
            sentences= list_to_string(text)
            cleaned_sentence=proprocess_text_data(sentences)
            pipe_env=get_model("ESGBERT/EnvironmentalBERT-environmental" ,"text-classification")
            pipe_soc=get_model("ESGBERT/SocialBERT-social" ,"text-classification")
            pipe_gov=get_model("ESGBERT/GovernanceBERT-governance","text-classification")
            pipe_sent=get_model("climatebert/distilroberta-base-climate-sentiment","text-classification")
            pipe_other=get_model("nlptown/bert-base-multilingual-uncased-sentiment","nlptown/bert-base-multilingual-uncased-sentiment")
            for t in cleaned_sentence:
                sentences_class.append(t)
                label,score_class=classify_sentence_label(t,pipe_env,pipe_soc,pipe_gov)
                labels_class.append(label)
                scores_classes.append(score_class)
                if label=="environmental":
                    sentiment_env = pipe_sent([t])
                    labels_sent.append(sentiment_env[0]['label'])
                else:
                    sentiment_env = pipe_other([t])
                    labels_sent.append(get_sentiment(sentiment_env[0]['label']))
                scores_sent.append(sentiment_env[0]['score'])
            data={
                "factors":sentences_class,
                "category":labels_class,
                "score_class":scores_classes,
                "sentiment":labels_sent,
                "score_sentiment":scores_sent,
                
            }
            all_data_sentiment = pd.DataFrame(data)
            all_data_sentiment[['e_score', 's_score', 'g_score']] = all_data_sentiment.apply(calculate_esg_scores, axis=1, result_type='expand')
            all_data_sentiment = all_data_sentiment.to_dict(orient='records')
            #####
            # entity=get_word_entity(cleaned_sentence)
            # campany_name=get_campany_name(entity)
            total_environmental_label, total_social_label,total_governance_label= get_classes(all_data_sentiment)
            total_environmental_neutral,total_environmental_risk,total_environmental_opportunity=get_sent_env(all_data_sentiment)
            total_social_neutral,total_social_risk,total_social_opportunity=get_sent_soc(all_data_sentiment)
            total_governance_neutral,total_governance_risk,total_governance_opportunity=get_sent_gov(all_data_sentiment)
            #######
            esg_score,total_e_score,total_s_score,total_g_score=calculate_total_esg(all_data_sentiment)
            document_data = {
                "campany_name": campany_name,
                "year": year,
                "total_env_label": total_environmental_label,
                "total_soc_label": total_social_label,
                "total_gov_label": total_governance_label,
                "total_env_neutral": total_environmental_neutral,
                "total_env_opportunity": total_environmental_opportunity,
                "total_env_risk": total_environmental_risk,
                "total_soc_neutral": total_social_neutral,
                "total_soc_opportunity": total_social_opportunity,
                "total_soc_risk": total_social_risk,
                "total_gov_neutral": total_governance_neutral,
                "total_gov_opportunity": total_governance_opportunity,
                "total_gov_risk": total_governance_risk,
                "total_e_score": total_e_score,
                "total_s_score": total_s_score,
                "total_g_score": total_g_score,
                "total_esg_score": esg_score
            }
            
            all_data={"all_data_sentiment":all_data_sentiment,"document_data":document_data}
            
            await self.save_system_usage(data)
            
            await self.send(json.dumps(all_data))
            # await self.delete_data()
            
            # Sleep for a while before sending the next data (adjust the interval as needed)
            await asyncio.sleep(1)