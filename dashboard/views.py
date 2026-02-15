from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Profile
from quizzes.models import Category, Subcategory 
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
    
    total_subs = Subcategory.objects.count()
    completed_count = profile.completed_subcategories.count()
    
    mastery_level = (completed_count / total_subs * 100) if total_subs > 0 else 0
    all_subcategories = Subcategory.objects.all()
    
    return render(request, 'quizzes/dashboard.html', {
        'profile': profile,
        'mastery_level': mastery_level,
        'all_subcategories': all_subcategories
    })
