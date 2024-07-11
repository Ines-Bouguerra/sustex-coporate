import asyncio
import logging
import json
import time
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chatbot.functions import define_question, fine_tune_model, get_response, save_file_json, split_data,fine_tune_model_task
from esganalyse.functions_csv import calculate_based_columns, calculate_based_lignes, calculate_esg_number, read_from_csv, read_from_xlsx, read_sheet_names
from .serializers import CampanySerializer,CampanyDetailsSerializer
from .models import Campany
from django.db.models import Q
from esganalyse.functions import analyse_sentence, extract_from_pdf,extract_text_page, generate_recommendation, get_content_first, get_date_report, get_file_extension, init_models,list_to_string,proprocess_text_data,get_model,classify_sentence_label,get_sentiment,get_word_entity,get_campany_name,calculate_total_esg,calculate_esg_scores,get_classes,get_sent_env,get_sent_soc,get_sent_gov, save_uploaded_file, translate_text
from django.core import serializers
from celery import shared_task
import re
logger = logging.getLogger(__name__) 
class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info('WebSocket connection established')
        await self.accept()
        await self.channel_layer.group_add(
            "chart_group_global",
            self.channel_name,
        )
        # asyncio.create_task(self.send(json.dumps({"msg":"hello from backend!"})))
        
    # async def receive(self, text_data):
    #     # print(self.scope['file'])
    #     print(text_data)
    #     text_data_json = json.loads(text_data)
    #     print(text_data_json)
    #     text_data_json=text_data_json['data']
    #     file_path = text_data_json.get('file_path')
    #     msg = text_data_json.get('msg',None)
    #     print("save uploaded file",file_path)
    #     saved_file_path=file_path
    #     saved_file_path=saved_file_path.strip('/')  if saved_file_path is not None else None
    #     if saved_file_path is not None:
    #         if get_file_extension(saved_file_path)==".pdf":
    #             all_data=await self.get_info_pdf(saved_file_path)
    #         elif get_file_extension(saved_file_path)==".csv":
    #             all_data=await self.get_info_csv(saved_file_path)
    #         elif get_file_extension(saved_file_path)==".xlsx":
    #            all_data=await self.get_info_xlsx(saved_file_path)
    #         await self.send(json.dumps(all_data))
    #         await self.save_system_usage(all_data['all_data_sentiment'],all_data['document_data'])
    #         await asyncio.sleep(1)
    #         fine_tune_model_task.delay(all_data['document_data'])
    #     if msg is not None :
    #         model_fine_tune = "fine-tuned-gpt2"
    #         asyncio.create_task(self.response_msg(msg,model_fine_tune))
    async def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        print(text_data_json)
        text_data_json = text_data_json['data']
        file_path = text_data_json.get('file_path')
        msg = text_data_json.get('msg', None)
        print("save uploaded file", file_path)
        saved_file_path = file_path
        saved_file_path = saved_file_path.strip('/') if saved_file_path is not None else None

        async def process_file(saved_file_path):
            if get_file_extension(saved_file_path) == ".pdf":
                await self.get_info_pdf(saved_file_path)
            elif get_file_extension(saved_file_path) == ".csv":
                await self.get_info_csv(saved_file_path)
            elif get_file_extension(saved_file_path) == ".xlsx":
               await self.get_info_xlsx(saved_file_path)

        if saved_file_path is not None:
            await process_file(saved_file_path)

        if msg is not None:
            print("helloooooo")
            model_fine_tune = "fine-tuned-gpt2"
            response_task = asyncio.create_task(self.response_msg(msg, model_fine_tune))
            await response_task

            # # Re-run the file processing part
            # if saved_file_path is not None:
            #     await process_file(saved_file_path)

            
    
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
    
    ##function to save in database asynchrononsly
    @database_sync_to_async
    def save_system_usage(self, all_data_sentiment,document_data):
        # try:
            company_instance = Campany.objects.filter(
                Q(campany_name=document_data['campany_name']) & 
                Q(year=document_data['year'])
            ).first()
            
            if company_instance:
                dashboard_serializer = CampanySerializer(company_instance, data=document_data)
            else:
                dashboard_serializer = CampanySerializer(data=document_data)
            
            if dashboard_serializer.is_valid():
                dashboard_instance = dashboard_serializer.save()
                id_company = dashboard_instance.id
                print({"id_company": id_company})
                
                if id_company is not None:
                    for sentence in all_data_sentiment:
                        sentence['campany'] = id_company
                        sentence_serializer = CampanyDetailsSerializer(data=sentence)
                        
                        if sentence_serializer.is_valid():
                            sentence_serializer.save()
                        else:
                            print({"error in adding company details": sentence_serializer.errors})
            else:
                print({"error in adding company": dashboard_serializer.errors})
        
       
      
          
    async def get_info_pdf(self,path):
        sentences_class=[]
        labels_class=[]
        scores_classes=[]
        labels_sent=[]
        scores_sent=[]
        doc= extract_from_pdf(path)
        text_first=get_content_first(0, 4,doc)
        campany_name=get_campany_name(text_first)
        year=get_date_report(text_first)
        print({"campany_name":campany_name,"year":year})
        for page in doc:
            text=extract_text_page(page)
            sentences= list_to_string(text)
            cleaned_sentence=proprocess_text_data(sentences)
            pipe_env,pipe_soc,pipe_gov,pipe_sent,pipe_other,pipe_esg=init_models()
            for t in cleaned_sentence:
                data=analyse_sentence(t,pipe_env,pipe_soc,pipe_gov,pipe_esg,pipe_sent,pipe_other,sentences_class,labels_class,scores_classes,labels_sent,scores_sent)
                all_data_sentiment = pd.DataFrame(data)
                all_data_sentiment[['e_score', 's_score', 'g_score','esg_score']] = all_data_sentiment.apply(calculate_esg_scores, axis=1, result_type='expand')
                #####
                total_environmental_label, total_social_label,total_governance_label= get_classes(all_data_sentiment)
                total_environmental_neutral,total_environmental_risk,total_environmental_opportunity=get_sent_env(all_data_sentiment)
                total_social_neutral,total_social_risk,total_social_opportunity=get_sent_soc(all_data_sentiment)
                total_governance_neutral,total_governance_risk,total_governance_opportunity=get_sent_gov(all_data_sentiment)
                #######
                total_esg_score,total_e_score,total_s_score,total_g_score=calculate_total_esg(all_data_sentiment)
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
                    "total_esg_score": total_esg_score
                }
                all_data_sentiment = all_data_sentiment.where(pd.notna(all_data_sentiment), None)
                all_data_sentiment = all_data_sentiment.to_dict(orient='records')
                all_data_sentiment = [{k: v if not pd.isna(v) else None for k, v in d.items()} for d in all_data_sentiment]
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
                all_data={"all_data_sentiment":all_data_sentiment,"document_data":document_data,"timestamp":unix_timestamp}
                await self.send(text_data=json.dumps(all_data))
                await self.save_system_usage(all_data['all_data_sentiment'], all_data['document_data'])
                await asyncio.sleep(1)
                fine_tune_model_task.delay(all_data['document_data'])
                
                
    async def get_info_csv(self,path):
        pipe_env,pipe_soc,pipe_gov,_,_,pipe_esg=init_models()
        df=read_from_csv(path)
        columns_list=df.columns.to_list()
        column_env,column_soc,column_gov=calculate_based_columns(df,columns_list,pipe_env, pipe_soc, pipe_gov, pipe_esg)
        if len(column_env)==0 or len(column_soc)!=0 or len(column_gov)!=0:
            df_res=calculate_esg_number(df,column_gov,column_soc,column_env)
        else:
            column_env,column_soc,column_gov,df_esg=calculate_based_lignes(df,pipe_env, pipe_soc, pipe_gov, pipe_esg)
            df_res=calculate_esg_number(df_esg,column_gov,column_soc,column_env)
        json_data = json.loads(df_res.to_json(orient='records'))
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
        total_esg_score,total_e_score,total_s_score,total_g_score=calculate_total_esg(json_data)
        document_data = {
                    "campany_name": None,
                    "year": None,
                    "total_env_label": 0,
                    "total_soc_label": 0,
                    "total_gov_label": 0,
                    "total_env_neutral": 0,
                    "total_env_opportunity": 0,
                    "total_env_risk": 0,
                    "total_soc_neutral": 0,
                    "total_soc_opportunity": 0,
                    "total_soc_risk": 0,
                    "total_gov_neutral": 0,
                    "total_gov_opportunity": 0,
                    "total_gov_risk": 0,
                    "total_e_score": total_e_score,
                    "total_s_score": total_s_score,
                    "total_g_score": total_g_score,
                    "total_esg_score": total_esg_score
                }
        all_data={"all_data_sentiment":json_data,"document_data":document_data,"timestamp":unix_timestamp}
        await self.send(json.dumps(all_data))
        await asyncio.sleep(1)
        
        
    async def get_info_xlsx(self,path):
        sheet_names=read_sheet_names(path)
        for sheet in sheet_names:
            pipe_env,pipe_soc,pipe_gov,_,_,pipe_esg=init_models()
            df=read_from_xlsx(path,sheet)
            columns_list=df.columns.to_list()
            column_env,column_soc,column_gov=calculate_based_columns(df,columns_list,pipe_env, pipe_soc, pipe_gov, pipe_esg)
            if len(column_env)==0 or len(column_soc)!=0 or len(column_gov)!=0:
                df_res=calculate_esg_number(df,column_gov,column_soc,column_env)
            else:
                column_env,column_soc,column_gov,df_esg=calculate_based_lignes(df,pipe_env, pipe_soc, pipe_gov, pipe_esg)
                df_res=calculate_esg_number(df_esg,column_gov,column_soc,column_env)
            json_data = json.loads(df_res.to_json(orient='records'))
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
            total_esg_score,total_e_score,total_s_score,total_g_score=calculate_total_esg(json_data)
            document_data = {
                        "campany_name": None,
                        "year": None,
                        "total_env_label": 0,
                        "total_soc_label": 0,
                        "total_gov_label": 0,
                        "total_env_neutral": 0,
                        "total_env_opportunity": 0,
                        "total_env_risk": 0,
                        "total_soc_neutral": 0,
                        "total_soc_opportunity": 0,
                        "total_soc_risk": 0,
                        "total_gov_neutral": 0,
                        "total_gov_opportunity": 0,
                        "total_gov_risk": 0,
                        "total_e_score": total_e_score,
                        "total_s_score": total_s_score,
                        "total_g_score": total_g_score,
                        "total_esg_score": total_esg_score
                    }
            all_data={"all_data_sentiment":json_data,"document_data":document_data,"timestamp":unix_timestamp}
            await self.send(json.dumps(all_data))
            await asyncio.sleep(1)
             
    async def response_msg(self,msg,model_fine_tune):
        msg=translate_text(msg,"en")
        response=get_response(model_fine_tune,msg)
        generated_text=response[0]['generated_text']
        # print("generated_text ===>" ,generated_text)
        parts = generated_text.split("chatbot:")
        answer = parts[1]
        print("firsttt answer ===>" ,answer)
        
        await self.send(json.dumps(answer))