#APP_URLS
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.custom_login, name='login'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/', views.custom_logout, name='logout'),
    path('zapasy/', views.zapasy, name='zapasy'),
    path('poradi-tymu/', views.poradi_tymu, name='poradi_tymu'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # Admin URLs
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/pridat-zapas/', views.pridat_zapas, name='pridat_zapas'),
    path('admin-panel/zadat-vysledek/<int:match_id>/', views.zadat_vysledek, name='zadat_vysledek'),
    path('admin-panel/vyhodnotit-poradi/', views.vyhodnotit_poradi, name='vyhodnotit_poradi'),
]