
import asyncio
from asgiref.sync import sync_to_async
import logging
import json
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
from django.db.models import Q
from django.core import serializers
from chatbot.functions import define_question, fine_tune_model, get_response, save_file_json, split_data
from esganalyse.models import Campany
logger = logging.getLogger(__name__) 
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info('WebSocket connection established')
        await self.accept()
        await self.channel_layer.group_add(
            "chart_group_global",
            self.channel_name,
        )
        # asyncio.create_task(self.send(json.dumps({"msg":"hello from backend!"})))
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        campany_name = text_data_json['campany_name']
        msg = text_data_json['msg']
        year = text_data_json['year']
        print(campany_name,year,msg)
        campany = await sync_to_async(Campany.objects.get)(Q(campany_name=campany_name) & Q(year=year))
        campany_dict = serializers.serialize("json", [campany])  # Serializing single object
        res = json.loads(campany_dict)
        campany_json = res[0]['fields']
        campany_json['id'] = res[0]['pk']
        if msg is not None:
            asyncio.create_task(self.response_msg(msg,campany_json))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
    
   

       
    async def response_msg(self,msg,data):
        file_path="data.json"
        model_fine_tune="fine-tuned-gpt2"
        list_question=define_question(data)
        save_file_json(file_path,list_question) 
        train_dataset,eval_dataset=split_data(file_path)
        fine_tune_model(train_dataset,eval_dataset,model_fine_tune)
        response=get_response(model_fine_tune,msg)
        await self.send(json.dumps(response))