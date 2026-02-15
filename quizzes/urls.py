from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category_list, name='quiz_categories'),
    path('categories/<int:category_id>/', views.subcategory_list, name='subcategories'),
    path('settings/<int:subcategory_id>/', views.quiz_settings, name='quiz_settings'),
    path('start/', views.start_quiz_engine, name='start_quiz_engine'),
    path('play/', views.start_quiz_engine, name='start_quiz_engine'),
    path('submit/', views.submit_quiz, name='submit_quiz'), 
]
