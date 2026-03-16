import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Count
from django.db.models import Avg, Count, Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from users.models import Profile
from quizzes.models import Category, QuizAttempt, Subcategory

def home(request):
    """Public home page showing all quiz categories."""
    context = {'categories': Category.objects.all()}
    return render(request, 'home.html', context)

@login_required(login_url='login')
def dashboard_home(request):
    """Simple redirect or landing for the dashboard namespace."""
    return render(request, 'dashboard/index.html')

@login_required
def dashboard(request):
    """
    Main Analytics Dashboard.
    Calculates mastery, streak, and prepares JSON data for Chart.js.
    """
    profile = request.user.profile 
    
    # 1. Mastery Logic: Based on subcategories completed by the user
    all_subcategories = Subcategory.objects.all()
    completed_subs = profile.completed_subcategories.all()
    completed_count = completed_subs.count()
    
    # Calculate percentage and round for clean UI display
    mastery_calc = (completed_count / all_subcategories.count() * 100) if all_subcategories.count() > 0 else 0
    
    # 2. Quiz Filtering
    user_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-created_at')
    
    # CHARTS & STATS: Only use quizzes that were successfully submitted
    completed_quizzes = user_attempts.filter(is_completed=True)
    
    # RESUME: Only quizzes that were started but not yet submitted
    incomplete_quizzes = user_attempts.filter(is_completed=False)

    # 3. Aggregate Statistics
    avg_score = completed_quizzes.aggregate(Avg('percentage'))['percentage__avg'] or 0
    best_score = completed_quizzes.aggregate(Max('percentage'))['percentage__max'] or 0

    # 4. Chart Data Preparation
    # Pie/Doughnut Chart: Distribution of quizzes across different subcategories
    category_data = completed_quizzes.values('subcategory_name').annotate(count=Count('id'))
    cat_labels = [item['subcategory_name'] for item in category_data]
    cat_counts = [item['count'] for item in category_data]
    
    # Line Chart: Score trends over the last 10 completed quizzes
    trends = completed_quizzes.order_by('created_at')[:10]
    trend_labels = [t.created_at.strftime("%d %b, %H:%M") for t in trends]
    trend_scores = [float(t.percentage) for t in trends]

    return render(request, 'dashboard/index.html', {
        'profile': profile,
        'mastery_level': round(mastery_calc, 1),
        'completed_count': completed_count,
        'total_quizzes': completed_quizzes.count(),
        'avg_score': round(avg_score, 1),
        'best_score': round(best_score, 1),
        'incomplete_quizzes': incomplete_quizzes,
        # JSON strings for the Chart.js script in the template
        'cat_labels_js': json.dumps(cat_labels),
        'cat_counts_js': json.dumps(cat_counts),
        'trend_labels_js': json.dumps(trend_labels),
        'trend_scores_js': json.dumps(trend_scores),
    })
    incomplete_quizzes = QuizAttempt.objects.filter(user=request.user, is_completed=False)

    return render(request, 'dashboard/index.html', {'incomplete_quizzes': incomplete_quizzes})

@login_required
def leaderboard(request):
    """
    Ranks users by their average score across all completed quizzes.
    Only users with at least one completed quiz are shown.
    """
    rankings = User.objects.annotate(
        # Calculate average only for completed quizzes
        avg_score=Avg('quizattempt__percentage', filter=Q(quizattempt__is_completed=True)),
        
        # Count only completed quizzes using a Q object
        completed_count=Count('quizattempt', filter=Q(quizattempt__is_completed=True))
    ).filter(completed_count__gt=0).order_by('-avg_score')[:10]
    
    return render(request, 'dashboard/leaderboard.html', {'rankings': rankings})

@login_required
def quiz_history(request):
    """
    Displays a paginated list of all completed quizzes with scores and dates.
    """
    attempts_list = QuizAttempt.objects.filter(
        user=request.user, 
        is_completed=True
    ).order_by('-created_at')
    
    # Pagination: Show 10 records per page
    paginator = Paginator(attempts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/history.html', {'page_obj': page_obj})
