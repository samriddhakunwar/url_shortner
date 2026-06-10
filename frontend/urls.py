from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Auth pages
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('register/', views.RegisterPageView.as_view(), name='register'),

    # App pages (require JWT in localStorage)
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('create/', views.CreateURLView.as_view(), name='create_url'),
    path('urls/', views.URLListView.as_view(), name='url_list'),
    path('urls/<int:pk>/edit/', views.EditURLView.as_view(), name='edit_url'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
]
