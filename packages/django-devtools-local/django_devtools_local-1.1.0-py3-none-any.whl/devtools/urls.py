from django.urls import path
from . import views

app_name = 'devtools'

urlpatterns = [
    # Page principale
    path('', views.IndexView.as_view(), name='index'),
    
    # Exploration des tables
    path('tables/', views.TablesView.as_view(), name='tables'),
    
    # Console de requêtes
    path('query/', views.QueryView.as_view(), name='query'),
    
    # Schéma de la base de données
    path('schema/', views.database_schema_view, name='schema'),
    
    # Fonctions des apps
    path('functions/', views.FunctionsView.as_view(), name='functions'),
    
    # APIs
    path('api/models/', views.ModelsAPIView.as_view(), name='api_models'),
    path('api/models/<str:app_label>/<str:model_name>/', 
         views.ModelDataAPIView.as_view(), name='api_model_data'),
] 