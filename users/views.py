from django.shortcuts import render, redirect
from .forms import RegistrationForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # encryption/hashing
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login') 
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def index(request):
    return render(request, 'users/index.html')