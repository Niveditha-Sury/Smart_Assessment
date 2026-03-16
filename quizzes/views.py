import random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Subcategory, Question, Choice
from .utils import generate_ai_questions 
from .models import QuizAttempt, Subcategory
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
    timer_enabled = request.POST.get('timer') == 'on'
    timer_duration = int(request.POST.get('timer_duration', 5)) if timer_enabled else 0
     

    if request.method == 'POST':
        request.session['quiz_config'] = {
            'subcategory_id': subcategory_id,
            'difficulty': request.POST.get('difficulty'),
            'num_questions': int(request.POST.get('num_questions')),
            'timer_enabled': timer_enabled,
            'time_limit': timer_duration * 60
        }
        attempt = QuizAttempt.objects.create(user=request.user)
        return redirect('start_quiz_engine', quiz_id=attempt.id)
    return render(request, 'quizzes/quiz_settings.html', {'subcategory': subcategory})

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
    # Fetch the existing attempt that was created when the quiz started
    attempt = get_object_or_404(QuizAttempt, id=quiz_id, user=request.user)
    
    if request.method == 'POST':
        score = 0
        total_questions = 0
        results = []
        
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

        # --- Scoring Logic ---
        if is_ai:
            ai_data = request.session.get('ai_quiz_data', [])
            total_questions = len(ai_data)
            for i, q in enumerate(ai_data):
                user_ans = request.POST.get(f'q{i+1}')
                correct_ans = q.get('correct_answer')
                is_correct = (user_ans == correct_ans)
                if is_correct: score += 1
                
                explanation = ""
                if not is_correct:
                    explanation = get_ai_explanation(q.get('text'), correct_ans)

                results.append({
                    'question': q.get('text'),
                    'user_choice': user_ans or "No Answer",
                    'correct_choice': correct_ans,
                    'is_correct': is_correct,
                    'explanation': explanation 
                })
        else:
            for key, value in request.POST.items():
                if key.startswith('q') and key[1:].isdigit():
                    q_id = key[1:]
                    try:
                        question = Question.objects.get(id=q_id)
                        total_questions += 1
                        correct_choice = question.choices.filter(is_correct=True).first()
                        user_choice = question.choices.filter(id=value).first()
                        is_correct = (correct_choice == user_choice)
                        if is_correct: score += 1
                        
                        explanation = ""
                        if not is_correct:
                            correct_text = correct_choice.text if correct_choice else "N/A"
                            explanation = get_ai_explanation(question.text, correct_text)

                        results.append({
                            'question': question.text,
                            'user_choice': user_choice.text if user_choice else "No Answer",
                            'correct_choice': correct_choice.text if correct_choice else "N/A",
                            'is_correct': is_correct,
                            'explanation': explanation 
                        })
                    except Question.DoesNotExist:
                        continue

        percentage = int((score / total_questions * 100)) if total_questions > 0 else 0

        # --- UPDATE THE EXISTING ATTEMPT ---
        # Instead of QuizAttempt.objects.create, we update the 'attempt' object
        attempt.subcategory_name = sub_name
        attempt.score = score
        attempt.total_questions = total_questions
        attempt.percentage = percentage
        attempt.difficulty = difficulty
        attempt.time_spent = time_spent
        attempt.is_ai = is_ai
        attempt.is_completed = True # Mark as finished
        attempt.save() # Save updates to DB

        # --- Profile & Streak Logic ---
        if request.user.is_authenticated:
            profile = request.user.profile
            profile.update_streak()
            
            if not is_ai and sub_id and percentage >= 50:
                subcategory = Subcategory.objects.filter(id=sub_id).first()
                if subcategory:
                    profile.completed_subcategories.add(subcategory)

        context = {
            'score': score,
            'total': total_questions,
            'percentage': percentage,
            'results': results,
            'difficulty': difficulty,
            'time_spent': time_spent,
            'is_ai': is_ai,
            'sub_name': sub_name,
            'status': "Pass" if percentage >= 50 else "Fail"
        }
        
        if is_ai:
            request.session.pop('ai_quiz_data', None)

        attempt.is_completed = True 
        attempt.save()

        return render(request, 'quizzes/result.html', context)

def process_ai_generation(request, sub_id):
    subcategory = get_object_or_404(Subcategory, id=sub_id)
    # Pull settings chosen by user in quiz_settings view
    config = request.session.get('quiz_config', {})
    difficulty = config.get('difficulty', 'Medium')
    num_questions = config.get('num_questions', 5)

    # Pass the actual user-selected difficulty and count to AI
    questions = generate_ai_questions(subcategory.name, difficulty, num_questions)
    
    if questions:
        request.session['ai_quiz_data'] = questions
        request.session['current_sub_id'] = sub_id
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Failed to reach AI server'})

def quiz_play_ai(request):
    questions = request.session.get('ai_quiz_data')
    sub_id = request.session.get('current_sub_id')
    config = request.session.get('quiz_config', {}) # Get the timer/difficulty config
    num_questions = int(config.get('num_questions', 5))

    if not questions:
        return redirect('quiz_categories')

    # Calculate time limit for AI mode exactly like standard engine
    timer_enabled = config.get('timer_enabled', False)
    time_limit = len(questions) * 60 if timer_enabled else 0

    context = {
        'questions': questions,
        'sub_id': sub_id,
        'is_ai': True,
        'timer_enabled': timer_enabled,
        'time_limit': time_limit,
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