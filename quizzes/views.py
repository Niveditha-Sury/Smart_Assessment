import random
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
# Consolidated Models (Remove duplicate Subcategory import)
from .models import Category, Subcategory, Question, Choice, QuizAttempt
# Only import generate_ai_questions (get_ai_explanation is now handled inside it)
from .utils import generate_ai_questions
from .utils import get_ai_explanation

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'quizzes/categories.html', {'categories': categories})

def subcategory_list(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = category.subcategories.all()
    return render(request, 'quizzes/subcategories.html', {
        'category': category,
        'subcategories': subcategories
    })

def quiz_settings(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    
    # 1. Capture the mode from the URL (?mode=ai) for the GET request
    mode_from_url = request.GET.get('mode', 'standard')

    if request.method == 'POST':
        # 2. Capture the mode from the hidden input for the POST request
        quiz_mode = request.POST.get('quiz_mode', 'standard')
        
        request.session['quiz_config'] = {
            'subcategory_id': subcategory_id,
            'difficulty': request.POST.get('difficulty'),
            'num_questions': int(request.POST.get('num_questions')),
            'timer_enabled': request.POST.get('timer') == 'on',
            'time_limit': int(request.POST.get('timer_duration', 5)) * 60,
        }
        
        # Create the attempt to prevent the "Battlefield" redirect
        attempt = QuizAttempt.objects.create(user=request.user)
        request.session['current_quiz_id'] = attempt.id
        request.session.modified = True
        request.session.save() 

        if quiz_mode == 'ai':
            return redirect('quiz_loading', sub_id=subcategory_id)
        
        return redirect('start_quiz_engine', quiz_id=attempt.id)

    # 3. CRITICAL: This return must be OUTSIDE the 'if POST' block 
    # to handle the initial page load (GET request).
    return render(request, 'quizzes/quiz_settings.html', {
        'subcategory': subcategory,
        'mode': mode_from_url
    })

def start_quiz_engine(request, quiz_id):
    attempt = get_object_or_404(QuizAttempt, id=quiz_id, user=request.user)
    
    # 1. Block access if already finished
    if attempt.is_completed:
        return redirect('dashboard:dashboard')
    
    config = request.session.get('quiz_config')
    if not config:
        return redirect('quiz_categories')

    sub_id = config.get('subcategory_id')
    
    # 2. Check if questions are already assigned in the session
    # This prevents the questions from changing if the user refreshes/resumes
    assigned_ids = request.session.get('quiz_question_ids')

    if assigned_ids:
        # Fetch the specific questions already stored in the session
        selected_questions = Question.objects.filter(id__in=assigned_ids)
        # Order them to match the session list order
        selected_questions = sorted(selected_questions, key=lambda q: assigned_ids.index(q.id))
    else:
        # First time starting this quiz session: pick new questions
        all_questions = Question.objects.filter(
            subcategory_id=sub_id,
            difficulty=config.get('difficulty')
        )
        questions_list = list(all_questions)
        num_to_pick = min(len(questions_list), int(config.get('num_questions', 5)))
        selected_questions = random.sample(questions_list, num_to_pick) if questions_list else []
        
        # Save these IDs so they persist during a "Resume"
        request.session['quiz_question_ids'] = [q.id for q in selected_questions]
        request.session['user_answers'] = {}

    num_to_pick = len(selected_questions)
    timer_enabled = config.get('timer_enabled', False)
    time_limit = num_to_pick * 60 if timer_enabled else 0
   
    context = {
        'questions': selected_questions,
        'sub_id': sub_id,
        'is_ai': False,
        'timer_enabled': timer_enabled,
        'time_limit': time_limit, 
        'attempt': attempt, # Passing the ID 24 here
    }
    return render(request, 'quizzes/quiz_play.html', context)
                    
def quiz_step(request, step):
    question_ids = request.session.get('quiz_question_ids', [])
    if not question_ids or step >= len(question_ids):
        return redirect('submit_quiz') 

    q_id = question_ids[step]
    question = get_object_or_404(Question, id=q_id)
    
    # Check if user already answered this (for 'Previous' button support)
    user_answers = request.session.get('user_answers', {})
    selected_choice_id = user_answers.get(str(q_id))

    context = {
        'question': question,
        'step': step,
        'total': len(question_ids),
        'progress': int(((step + 1) / len(question_ids)) * 100),
        'selected_choice_id': selected_choice_id,
        'is_last': step == len(question_ids) - 1,
    }
    return render(request, 'quizzes/quiz_play.html', context)

def submit_quiz(request, quiz_id):
    attempt = get_object_or_404(QuizAttempt, id=quiz_id, user=request.user)
    
    if request.method != 'POST':
        return redirect('quiz_categories')

    score = 0
    total_questions = 0
    results = []
    
    # Metadata Retrieval
    config = request.session.get('quiz_config', {})
    sub_id = config.get('subcategory_id')
    difficulty = config.get('difficulty', 'Medium')
    time_spent = request.POST.get('time_spent', '00:00')
    is_ai = request.POST.get('is_ai') in ['True', 'true', True]

    sub_name = "AI Generated Quiz"
    if not is_ai and sub_id:
        subcategory = Subcategory.objects.filter(id=sub_id).first()
        if subcategory:
            sub_name = subcategory.name

    # --- SCORING & EXPLANATION LOGIC ---
    if is_ai:
        # AI Mode: Explanations are pre-generated by Groq in the session
        ai_data = request.session.get('ai_quiz_data', [])
        total_questions = len(ai_data)
        for i, q in enumerate(ai_data):
            user_ans = request.POST.get(f'q{i+1}')
            correct_ans = q.get('correct_answer')
            is_correct = (user_ans == correct_ans)
            if is_correct: score += 1
            
            results.append({
                'question': q.get('text'),
                'user_choice': user_ans or "No Answer",
                'correct_choice': correct_ans,
                'is_correct': is_correct,
                'explanation': q.get('explanation', "Insight provided by AI engine.") 
            })
    else:
        # Standard Mode: Hybrid Logic (DB + Groq)
        for key, value in request.POST.items():
            if key.startswith('q') and key[1:].isdigit():
                q_id = key[1:]
                try:
                    question = Question.objects.get(id=q_id)
                    total_questions += 1
                    
                    correct_choice = question.choices.filter(is_correct=True).first()
                    user_choice = question.choices.filter(id=value).first()
                    
                    is_correct = (correct_choice.id == int(value)) if correct_choice and user_choice else False
                    if is_correct: score += 1
                    
                    # --- GROQ INTEGRATION FOR STANDARD MODE ---
                    # If DB has an explanation, use it. If not, ask Groq.
                    explanation = question.explanation
                    if not explanation and not is_correct and correct_choice:
                        try:
                            explanation = get_ai_explanation(question.text, correct_choice.text)
                        except Exception:
                            explanation = "Keep studying to master this topic!"
                    
                    results.append({
                        'question': question.text,
                        'user_choice': user_choice.text if user_choice else "No Answer",
                        'correct_choice': correct_choice.text if correct_choice else "N/A",
                        'is_correct': is_correct,
                        'explanation': explanation or "Great job! You mastered this concept."
                    })
                except (Question.DoesNotExist, ValueError):
                    continue

    # --- UPDATE ATTEMPT & GAMIFICATION ---
    percentage = int((score / total_questions * 100)) if total_questions > 0 else 0
    attempt.subcategory_name = sub_name
    attempt.score = score
    attempt.total_questions = total_questions
    attempt.percentage = percentage
    attempt.time_spent = time_spent
    attempt.is_ai = is_ai
    attempt.is_completed = True 
    attempt.save() 

    if request.user.is_authenticated:
        profile = request.user.profile
        profile.update_streak() 
        if not is_ai and sub_id and percentage >= 50:
            subcategory = Subcategory.objects.filter(id=sub_id).first()
            if subcategory:
                profile.completed_subcategories.add(subcategory)

    # --- FINAL RENDER & CLEANUP ---
    context = {
        'score': score, 'total': total_questions, 'percentage': percentage,
        'results': results, 'difficulty': difficulty, 'time_spent': time_spent,
        'is_ai': is_ai, 'sub_name': sub_name, 'status': "Pass" if percentage >= 50 else "Fail"
    }
    
    # Cleanup keys to reset state for the next quiz
    for key in ['ai_quiz_data', 'quiz_config', 'current_quiz_id']:
        request.session.pop(key, None)

    return render(request, 'quizzes/result.html', context)


def process_ai_generation(request, sub_id):
    subcategory = get_object_or_404(Subcategory, id=sub_id)
    config = request.session.get('quiz_config', {})
    difficulty = config.get('difficulty', 'Medium')
    num_questions = config.get('num_questions', 5)

    # The utility now returns a list of dicts: [{'text':..., 'explanation':...}, ...]
    questions = generate_ai_questions(subcategory.name, difficulty, num_questions)
    
    if questions:
        request.session['ai_quiz_data'] = questions
        request.session['current_sub_id'] = sub_id
        request.session.modified = True
        request.session.save()
        # Send the redirect URL back to the frontend
        return JsonResponse({
            'status': 'success', 
            'redirect_url': reverse('quiz_play_ai') 
        })
    
    return JsonResponse({'status': 'error', 'message': 'Failed to reach AI server'})

def quiz_play_ai(request):
    questions = request.session.get('ai_quiz_data')
    sub_id = request.session.get('current_sub_id')
    config = request.session.get('quiz_config', {})
    
    # Get the specific ID we stored in quiz_settings
    quiz_id = request.session.get('current_quiz_id')
    
    if not questions or not quiz_id:
        return redirect('quiz_categories')

    # Fetch the exact attempt or 404
    attempt = get_object_or_404(QuizAttempt, id=quiz_id, user=request.user)

    timer_enabled = config.get('timer_enabled', False)
    time_limit = len(questions) * 60 if timer_enabled else 0

    context = {
        'questions': questions,
        'sub_id': sub_id,
        'is_ai': True,
        'timer_enabled': timer_enabled,
        'time_limit': time_limit,
        'attempt': attempt, 
    }
    return render(request, 'quizzes/quiz_play.html', context)

def quiz_loading_page(request, sub_id):
    subcategory = get_object_or_404(Subcategory, id=sub_id)
    return render(request, 'quizzes/loading.html', {'subcategory': subcategory})

def save_answer(request, step):
    if request.method == "POST":
        choice_id = request.POST.get('choice')
        question_ids = request.session.get('quiz_question_ids', [])
        q_id = str(question_ids[step])

        # Store answer in session
        user_answers = request.session.get('user_answers', {})
        user_answers[q_id] = choice_id
        request.session['user_answers'] = user_answers
        request.session.modified = True

        # Decide where to go next
        if step + 1 < len(question_ids):
            return redirect('quiz_step', step=step + 1)
        else:
            return redirect('submit_quiz')
    return redirect('quiz_categories')

def quiz_history(request):
    """Fetches all completed quizzes for the logged-in user."""
    history_list = QuizAttempt.objects.filter(
        user=request.user, 
        is_completed=True
    ).order_by('-id')
    return render(request, 'dashboard/history.html', {'history': history_list})

def retake_quiz(request, attempt_id):
    """Creates a new attempt based on a previous one."""
    old_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    new_attempt = QuizAttempt.objects.create(
        user=request.user,
        subcategory_name=old_attempt.subcategory_name,
        difficulty=old_attempt.difficulty,
        score=0,
        total_questions=0,
        percentage=0.0,
        is_completed=False
    )
    return redirect('start_quiz_engine', quiz_id=new_attempt.id)

@csrf_exempt 
def complete_subcategory(request, sub_id):
    if request.method == 'POST':
        return HttpResponse(status=200)
    return HttpResponse(status=400)