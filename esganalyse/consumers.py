import asyncio
import logging
import json
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from esganalyse.functions import extract_from_pdf,extract_text_page,list_to_string,proprocess_text_data,get_model,classify_sentence_label,get_sentiment,get_word_entity,get_campany_name,calculate_total_esg,calculate_esg_scores,get_classes,get_sent_env,get_sent_soc,get_sent_gov
logger = logging.getLogger(__name__) 
class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info('WebSocket connection established')
        await self.accept()
        await self.channel_layer.group_add(
            "chart_group_global",
            self.channel_name,
        )
        asyncio.create_task(self.start_data_loop_global_chart())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
    
    ##function to save in database asynchrononsly
    # @database_sync_to_async
    # def save_system_usage(self, data):
    # # Create a serializer instance
    #     Dashboardserializer = MonitoringDataSerializer(data=data)
    #     # Check if the data is valid
    #     if Dashboardserializer.is_valid():
    #         # Check the count of existing entries
    #         count = MonitoringData.objects.count()
    #         # If the count exceeds 20, delete the oldest entry
    #         if count >= 20:
    #             # Find the record with the minimum timestamp and delete it
    #             min_timestamp_record = MonitoringData.objects.order_by('timestamp').first()
    #             if min_timestamp_record:
    #                 min_timestamp_record.delete()
    #         # Save the new data
    #         Dashboardserializer.save()
       
    async def start_data_loop_global_chart(self):
        path="../resources/orange_rapport-annuel-integre-2022.pdf"
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
                "sentence":sentences_class,
                "label":labels_class,
                "score_class":scores_classes,
                "sent_label":labels_sent,
                "score_sent_label":scores_sent
            }
            all_data_sentiment = pd.DataFrame(data)
            all_data_sentiment[['E_score', 'S_score', 'G_score']] = all_data_sentiment.apply(calculate_esg_scores, axis=1, result_type='expand')
            all_data_sentiment = all_data_sentiment.to_json(orient='records')
            #####
            entity=get_word_entity(cleaned_sentence)
            campany_name=get_campany_name(entity)
            total_environmental_label, total_social_label,total_governance_label= get_classes(all_data_sentiment)
            total_environmental_neutral,total_environmental_risk,total_environmental_opportunity=get_sent_env(all_data_sentiment)
            total_social_neutral,total_social_risk,total_social_opportunity=get_sent_soc(all_data_sentiment)
            total_governance_neutral,total_governance_risk,total_governance_opportunity=get_sent_gov(all_data_sentiment)
            #######
            esg_score,total_e_score,total_s_score,total_g_score=calculate_total_esg(all_data_sentiment)
            document_data = {
                "campany name": campany_name,
                "year": 2022,
                "Total environmental label": total_environmental_label,
                "Total social label": total_social_label,
                "Total governance label": total_governance_label,
                "Total environmental neutral": total_environmental_neutral,
                "Total environmental opportunity": total_environmental_opportunity,
                "Total environmental risk": total_environmental_risk,
                "Total social neutral": total_social_neutral,
                "Total social opportunity": total_social_opportunity,
                "Total social risk": total_social_risk,
                "Total governance neutral": total_governance_neutral,
                "Total governance opportunity": total_governance_opportunity,
                "Total governance risk": total_governance_risk,
                "Total_E_score": total_e_score,
                "Total_S_score": total_s_score,
                "Total_G_score": total_g_score,
                "ESG_score": esg_score
            }
            all_data={"all_data_sentiment":all_data_sentiment,"document_data":document_data}
                
            await self.send(json.dumps(all_data))
            # await self.delete_data()
            
            # Sleep for a while before sending the next data (adjust the interval as needed)
            await asyncio.sleep(1)