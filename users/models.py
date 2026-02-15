from django.db import models
from django.contrib.auth.models import User
from quizzes.models import Subcategory 

class Profile(models.Model):
    """
    Extends the base Django User model with additional details
    required for the Smart Assessment System.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile information
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default.png', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Gamification/Activity Metrics
    streak = models.IntegerField(default=0)
    last_activity = models.DateField(auto_now=True)
    
    # Mastery Tracking
    # This allows users to "unlock" or "complete" subcategories
    completed_subcategories = models.ManyToManyField(Subcategory, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def mastery_percentage(self):
        """
        Calculates the completion percentage based on total subcategories available.
        """
        total = Subcategory.objects.count()
        if total == 0:
            return 0
        completed = self.completed_subcategories.count()
        return (completed / total) * 100