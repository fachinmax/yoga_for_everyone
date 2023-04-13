from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('<int:pk>/', views.auction_detail, name="auction_detail"),
    path('<int:pk>/register/<int:bid>/<str:address>', views.save_bids),
    path('<int:pk>/allBids', views.get_bids),
    path('history/<str:address>', views.get_history),
    path('send-ether/<str:address>', views.get_auctions_winned),
    path('<int:pk>/price', views.get_price),
    path('hash/<str:hash>/<int:pk>', views.save_hash_payament),
    path('images/<str:address>', views.get_images),
    path('images/<str:address>/<int:pk>', views.upload_images)
]
