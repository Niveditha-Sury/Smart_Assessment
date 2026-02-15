from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required  
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm  
from .models import Profile




def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login') 
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def index(request):
    return render(request, 'users/index.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user is not None:
                login(request, user) 
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('home')  
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)  
    messages.info(request, "You have successfully logged out.")
    return redirect('login') 

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        new_email = request.POST.get('email')
        
        # Only update email if it's not empty
        if new_email:
            user.email = new_email
        
        user.first_name = request.POST.get('first_name', user.first_name)
        user.save()

        profile = user.profile
        profile.bio = request.POST.get('bio', profile.bio)
        profile.location = request.POST.get('location', profile.location)
        
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES.get('profile_pic')
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'users/profile.html')

@login_required
def dashboard(request):
    profile = request.user.profile
    from .models import Subcategory
    total_subs = Subcategory.objects.count()
    completed_count = profile.completed_subcategories.count()
    mastery_level = (completed_count / total_subs * 100) if total_subs > 0 else 0
    
    return render(request, 'quizzes/dashboard.html', {
        'profile': profile,
        'mastery_level': mastery_level
    })