from django.urls import path

from . import views

app_name = 'recompensas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
