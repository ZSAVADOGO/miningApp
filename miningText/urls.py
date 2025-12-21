from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Page principale (liste + div droite vide)
    path('transform/', views.transform, name='transform'),

    # AJAX uniquement (PAS de page complète)
    path('ajax/article/<int:id>/', views.transform_ajax, name='transform_ajax'),        # AJAX
    #path('ajax/article/<int:id>/', views.transform, name='transform'),
    
    path('article/<int:id>/', views.detail, name='detail'),
    path('create/', views.create, name='create'),
    path('update/<int:id>/', views.update, name='update'),
    path('delete/<int:id>/', views.delete, name='delete'),
    #path("ajax/search/", views.search_articles, name="search_articles"),
    path("search/", views.search_articles, name="article_search"),
    path("search_index/", views.search_articles_index, name="search_articles_index"),


        # Route AJAX pour récupérer le détail d’un article
    #path('ajax/article/<int:article_id>/', views.transform, name='transform'),
]