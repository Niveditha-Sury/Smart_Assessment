import random
from django.shortcuts import render, get_object_or_404
from .models import Category, Subcategory
from django.shortcuts import render, redirect
from .models import Question, Choice


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'quizzes/categories.html', {'categories': categories})

def subcategory_list(request, category_id):
    category = Category.objects.get(id=category_id)
    subcategories = category.subcategories.all()
    return render(request, 'quizzes/subcategories.html', {
        'category': category,
        'subcategories': subcategories
    })


def quiz_settings(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    
    if request.method == 'POST':
        # Store preferences temporarily in the browser session
        request.session['quiz_config'] = {
            'subcategory_id': subcategory_id,
            'difficulty': request.POST.get('difficulty'),
            'num_questions': int(request.POST.get('num_questions')),
            'timer_enabled': request.POST.get('timer') == 'on'
        }
        
        return redirect('start_quiz_engine') 
        
    return render(request, 'quizzes/quiz_settings.html', {'subcategory': subcategory})


def start_quiz_engine(request):
    config = request.session.get('quiz_config')
    
    if not config:
        return redirect('quiz_categories')

    # Filter questions based on Task 6 settings
    all_questions = Question.objects.filter(
        subcategory_id=config.get('subcategory_id'),
        difficulty=config.get('difficulty')
    )

    questions_list = list(all_questions)
    num_to_pick = min(len(questions_list), int(config.get('num_questions', 5)))
    
    if questions_list:
        selected_questions = random.sample(questions_list, num_to_pick)
    else:
        selected_questions = []

    context = {
        'questions': selected_questions,
        'timer_enabled': config.get('timer_enabled', False), 
        'time_limit': num_to_pick * 60 if config.get('timer_enabled') else 0,
    }
    return render(request, 'quizzes/quiz_play.html', context)

def submit_quiz(request):
    if request.method == 'POST':
        score = 0
        total_questions = 0
        results = []

        
        for key, value in request.POST.items():
            if key.startswith('q'):
                total_questions += 1
                q_id = key.replace('q', '')
                question = Question.objects.get(id=q_id)
                correct_choice = question.choices.filter(is_correct=True).first()
                user_choice = question.choices.filter(id=value).first()
                
                is_correct = (correct_choice == user_choice)
                if is_correct: score += 1
                
                results.append({
                    'question': question.text,
                    'user_choice': user_choice.text if user_choice else "None",
                    'correct_choice': correct_choice.text if correct_choice else "N/A",
                    'is_correct': is_correct
                })

        percentage = (score / total_questions * 100) if total_questions > 0 else 0

        
        context = {
            'score': score,
            'total': total_questions,
            'percentage': int(percentage), # Use int() to keep CSS clean
            'results': results
        }
        return render(request, 'quizzes/quiz_results.html', context)
    
    return redirect('quiz_categories')