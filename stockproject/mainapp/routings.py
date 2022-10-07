from django.urls import path,re_path
from .consumers import StockConsumer

websocket_urlpatters = {
    # room_name is dict key which we pass from views
   re_path(r"ws/stock/(?P<room_name>\w+)/$", StockConsumer.as_asgi()) 
}