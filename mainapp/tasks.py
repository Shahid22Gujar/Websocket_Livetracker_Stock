from zoneinfo import available_timezones
from celery import shared_task
from yahoo_fin.stock_info import tickers_nifty50,get_quote_table
from threading import Thread
import queue
from channels.layers import get_channel_layer
import asyncio
import simplejson 
import datetime
@shared_task(bind=True)
def update_stock(self,stockpicker:list = []): #stockpikcer are list of stocks picked by users
    data={}
    available_stocks=tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            stockpicker.remove(i)
    n_threads=len(stockpicker)
    thread_list=[]
    que=queue.Queue()
    for i in range(n_threads):
        #ase json doesnot suppport Nan type so ignore Nan value ,json.dumps bind the data and gives the string format
        thread=Thread(target=lambda q,args1: q.put({stockpicker[i]:simplejson.loads(simplejson.dumps(get_quote_table(args1),ignore_nan=True,default=datetime.datetime.isoformat))}),args=(que,stockpicker[i],))
        thread_list.append(thread)
        thread_list[i].start()
    
    for thread in thread_list:
        thread.join()
    
    while not que.empty():
        result=que.get()
        data.update(result)
    print(data)

    #send data to group
    channel_layer=get_channel_layer()
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(channel_layer.group_send('stock_track',{
        'type':'send_stock_update', # stock_update function is being called
        'message':data
    }))

    return "Done"
