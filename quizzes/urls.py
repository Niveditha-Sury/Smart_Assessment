from django.urls import path
from . import views

urlpatterns = [
    # Navigation
    path('categories/', views.category_list, name='quiz_categories'),
    path('categories/<int:category_id>/', views.subcategory_list, name='subcategories'),
    
    # Mode 1: Standard (Database) Quiz
    path('settings/<int:subcategory_id>/', views.quiz_settings, name='quiz_settings'),
    path('take/<int:quiz_id>/', views.start_quiz_engine, name='start_quiz_engine'),
    path('submit/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
    path('step/<int:step>/', views.quiz_step, name='quiz_step'),
    path('save-answer/<int:step>/', views.save_answer, name='save_answer'),
    path('history/', views.quiz_history, name='quiz_history'),
    path('retake/<int:attempt_id>/', views.retake_quiz, name='retake_quiz'),
    
    # Mode 2: AI (Groq) Quiz
    path('quiz/loading/<int:sub_id>/', views.quiz_loading_page, name='quiz_loading'),
    path('quiz/generate-logic/<int:sub_id>/', views.process_ai_generation, name='process_ai_generation'),
    path('quiz/play-ai/', views.quiz_play_ai, name='quiz_play_ai'),
    
    # Shared Utility
    path('complete-subcategory/<int:sub_id>/', views.complete_subcategory, name='complete_subcategory'),
]