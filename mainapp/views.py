from django.http import HttpResponse
import time
from django.shortcuts import render
from threading import Thread
import queue
from yahoo_fin.stock_info import *
from yahoo_fin.options import get_calls
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async

# Create your views here.
def stockpicker(request):
    dhfl=get_data('TEXRAIL.NS',start_date='06/01/2009',end_date=None,interval='1d')
    print(dhfl)
    # print('RELINACE.NS',)
    stock_picker=tickers_nifty50()
    print(stock_picker)
    context={'stockpicker': stock_picker}
    return render(request,'mainapp/stockpicker.html',context)

#note if we are running on asgi server then use async function always

@sync_to_async
def check_authenticated(request):
    print(request.user.is_authenticated,"User in view")
    if not request.user.is_authenticated:
        return False
    else:
        return True

# @login_required(login_url='/')
async def stocktracker(request):
    is_logged_in=await check_authenticated(request) #aysnc function ma await must
    print(is_logged_in),"isloggged in"
    if not is_logged_in:
        return HttpResponse('<h2>Please logged in</h2')

    stockpicker=request.GET.getlist('stockpicker')

    data={}
    available_stock=tickers_nifty50()
    for i in stockpicker:
        if i in available_stock:
           pass
            # data.update()
        else:
            return HttpResponse("Error")
    n_threads=len(stockpicker)
    que=queue.Queue()
    thread_list=[]
    for i in range(n_threads):
        thread=Thread(target = lambda q,args1: q.put({stockpicker[i]:get_quote_table(args1)}),args=(que,stockpicker[i]))

        thread_list.append(thread)
        thread_list[i].start()
    
    for thread in thread_list:

        thread.join()
    start = time.time()
    while not que.empty():
        result=que.get()
        data.update(result)
    start = time.time()
    # for i in stockpicker:
    #     print(i)
    #     detail=get_quote_table(i)

    #     data.update({i:detail})
    time_taken=time.time()-start
    
    # print(data)
    context={'data':data,'room_name':'track'}
    return render(request,'mainapp/stocktracker.html',context)
    