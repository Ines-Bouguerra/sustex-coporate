
import asyncio
import logging
import json
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
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
        msg = text_data_json['msg']
    
        if msg is not None:
            asyncio.create_task(self.response_msg(msg))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
    
   

       
    async def response_msg(self,msg):
        # Load pre-trained GPT-2 model and tokenizer
        model_name = "gpt2"
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)
        # Tokenize input
        input_ids = tokenizer.encode(msg, return_tensors="pt")
        # Generate response based on the input
        with torch.no_grad():
            output = model.generate(input_ids, max_length=100, pad_token_id=tokenizer.eos_token_id)

        # Decode and return response
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        await self.send(json.dumps(response))