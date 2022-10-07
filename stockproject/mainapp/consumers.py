
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async,async_to_sync
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from .models import StockDetail
import copy

class StockConsumer(AsyncWebsocketConsumer):

    @sync_to_async
    def add_to_celerybeat(self,stockpicker): # this is sync function
        # pass
        task=PeriodicTask.objects.filter(name='every-10-seconds')
        print(task)
        if len(task)>0:
            task=task.first()
            print(task.args)
            args=json.loads(task.args)
            print(args)
            args=args[0]
            for x in stockpicker:
                if x not in args:
                    args.append(x)
            task.args=json.dumps([args])
            task.save()
        else:
            schedule,create=IntervalSchedule.objects.get_or_create(every=10,period=IntervalSchedule.SECONDS)
            task=PeriodicTask.objects.create(interval=schedule,name='every-10-seconds',task='mainapp.update_stock',args=json.dumps([stockpicker]))
                

        # print(task)
    @sync_to_async
    def add_to_stockdetail(self,stockpicker):
        user=self.scope['user'] # getting logged in user
        print(user,"User")
        for i in stockpicker:
            stock,create=StockDetail.objects.get_or_create(stock=i)
            stock.user.add(user)


    async def connect(self):
       
        self.room_name=self.scope['url_route']['kwargs']['room_name']
        self.group_name= f'stock_{self.room_name}' 
        print(self.group_name,"Group")
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name #here should be channel name not room_name
        )

        #parse query_string 
        # print(parse_qs(self.scope['query_string']),'its in binary format' )
        query_param=parse_qs(self.scope['query_string'].decode())
        # print(query_param,"Query params")
        stockpicker=query_param.get('stockpicker')
        # print(stockpicker)

        # adding to stocks to celery beat
        await self.add_to_celerybeat(stockpicker) 

        #add user to stockdetails
        await self.add_to_stockdetail(stockpicker)

        await self.accept() # to accept connection
    
    @sync_to_async
    def helper_function(self):
        user=self.scope['user']
        print(user)
        stocks=StockDetail.objects.filter(user__id=user.id)
        task=PeriodicTask.objects.filter(name='every-10-seconds')
        args=json.load(task.args)
        args=args[0]
        for i in stocks:
            i.user.remove(user)
            # if there is no users associated with that stock then delete that stock for args
            if i.user.count() == 0: 
                args.remove(i.stock) # removing stock name from args
                i.delete() # deleting that object of models from db
        if args == None:
            args = []
        
        if len(args)==0: # if args is empty then delete that task from celery
            task.delet()
        else:
            task.args = json.load([args]) # else remaining stock save to celery databases 
            task.save()


    async def disconnect(self,close_code):
        
        await self.helper_function()

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(self.group_name,"Receing")
        text_data_json=json.loads(text_data)
        print(text_data_json,"Receiving text data")
        message=text_data_json['message']
        
        #send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type':'send_update', # type => here is method name
                'message': message
            }
        )
       
    @sync_to_async
    def select_user_stocks(self):
        user=self.scope['user']
        # stock is field name of stockdetail model
        #flat=True to give the list only
        user_stock=user.stockdetail__set.values('stock',flat=True) 
        #if we directly pass this to async function then we will gent django ORM error
        #as we return sync to async and again we have to convert in list to avoid sync ORM errro
        return list(user_stock)


    async def send_stock_update(self,event):
        message=event['message'] 
        message=copy.copy(message) #otherwise it change actual event object
        #message is dictionary
        user_stocks = await self.select_user_stocks()
         
        keys=message.keys()
        for key in list(keys):
            if key in user_stocks:
                pass
            else:
                del message[key]

        print(event,"Event sending stock update")
        #send message to websocket
        '''await self.send(text_data=json.dumps(
            {
                'message': message
            }
            ))'''
    
        await self.send(text_data=json.dumps(message))

    

# chat/consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class StockConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         print(self.room_name)
#         self.room_group_name = 'chat_%s' % self.room_name

#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))