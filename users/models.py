from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Corrected import
from datetime import timedelta     # Required for streak calculation
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
    last_activity = models.DateField(null=True, blank=True)
    
    # Mastery Tracking
    completed_subcategories = models.ManyToManyField(Subcategory, blank=True)

    def update_streak(self):
        # Now using django.utils.timezone.now()
        today = timezone.now().date()
        
        if self.last_activity is None:
            # First time ever playing
            self.streak = 1
        elif self.last_activity == today:
            # Already played today, do nothing to streak
            return
        elif self.last_activity == today - timedelta(days=1):
            # Played yesterday, increment streak
            self.streak += 1
        else:
            # Missed at least one day, reset streak to 1
            self.streak = 1
            
        self.last_activity = today
        self.save()

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