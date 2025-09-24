from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('config/<int:config_id>/', views.voucher_config_detail, name='config_detail'),
    path('config/<int:config_id>/test/', views.test_dynamic_form, name='test_form'),
    path('api/schema/<int:config_id>/', views.schema_preview, name='schema_api'),
]