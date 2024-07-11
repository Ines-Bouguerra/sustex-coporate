
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
from chatbot.functions import  get_response, translate_text
from esganalyse.models import Campany
import re
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
        text_data_json=text_data_json['data']
        msg = text_data_json.get('msg',None)
        if msg is not None:
            model_fine_tune = "fine-tuned-gpt2"
            asyncio.create_task(self.response_msg(msg,model_fine_tune))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
    
   

       
    async def response_msg(self,msg,model_fine_tune):
        msg=translate_text(msg,"en")
        response=get_response(model_fine_tune,msg)
        print(response)
        generated_text=response[0]['generated_text']
        match = re.search(r'Question:.*?\nAnswer: (.*?)(Answer:|$)', generated_text, re.DOTALL)
        # Extract the first answer if the pattern is found
        first_answer = match.group(1).strip() if match else None
        await self.send(json.dumps(first_answer))