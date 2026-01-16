from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle/<int:habit_id>/', views.toggle_habit, name='toggle_habit'),
    path('habit/<int:habit_id>/status/', views.habit_status, name='habit_status'),
    path('habit/<int:habit_id>/', views.habit_detail, name='habit_detail'),
    path('habit/<int:habit_id>/delete/', views.delete_habit, name='delete_habit'),
    path('habit/<int:habit_id>/delete/confirm/', views.confirm_delete_habit, name='confirm_delete_habit'),
    path('accounts/signup/', views.signup, name='signup'),
    path('habit/<int:habit_id>/insights/', views.habit_insights, name='habit_insights'),
]