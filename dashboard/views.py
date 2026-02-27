from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Profile
from quizzes.models import Category, QuizAttempt, Subcategory 
# Create your views here.

def home(request):
    context = {}
    if request.user.is_authenticated:
        context['categories'] = Category.objects.all()
    return render(request, 'home.html', context)

@login_required(login_url='login')
def dashboard_home(request):
    return render(request, 'dashboard/index.html')

@login_required
def dashboard(request):
    profile = request.user.profile 
    
    # Logic for Mastery Progress
    all_subcategories = Subcategory.objects.all()
    total_subs = all_subcategories.count()
    completed_count = profile.completed_subcategories.count()
    mastery_level = (completed_count / total_subs * 100) if total_subs > 0 else 0
    
    # Logic for Quiz History
    user_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-created_at')
    total_quizzes = user_attempts.count()
    
    return render(request, 'dashboard/index.html', {
        'profile': profile,
        'mastery_level': mastery_level,
        'all_subcategories': all_subcategories,
        'attempts': user_attempts,
        'total_quizzes': total_quizzes,
    })