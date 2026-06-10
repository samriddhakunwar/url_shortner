from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_url, name='create_url'),
    path('urls/', views.url_list, name='url_list'),
    path('urls/<int:pk>/edit/', views.edit_url, name='edit_url'),
    path('urls/<int:pk>/delete/', views.delete_url, name='delete_url'),
    path('analytics/', views.analytics, name='analytics'),
]
