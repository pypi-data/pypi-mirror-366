from django.urls import path
from . import views

app_name = 'log_hub'

urlpatterns = [
    path('', views.log_view, name='log_view'),
    path('change-language/', views.change_language, name='change_language'),
    path('clear/<str:log_file_name>/', views.clear_log, name='clear_log'),
    path('download/<str:log_file_name>/', views.download_log, name='download_log'),
]
