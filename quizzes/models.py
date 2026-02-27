from django.db import models
from django.contrib.auth.models import User
import json

class Category(models.Model):
    name = models.CharField(max_length=100) 
    icon_class = models.CharField(max_length=50, default="bi-list") # Bootstrap icon name
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
class Question(models.Model):
    DIFFICULTY_CHOICES = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    
    def __str__(self): return self.text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=255)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.IntegerField()
    difficulty = models.CharField(max_length=50)
    time_spent = models.CharField(max_length=10)
    is_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subcategory_name} - {self.score}"
    
class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)
    # Stores the list of Question IDs as a JSON string: [12, 45, 7, 22]
    question_ids = models.TextField() 
    # Stores user choices as JSON: {"12": "ChoiceA_ID", "45": "ChoiceB_ID"}
    user_answers = models.TextField(default='{}')
    current_index = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_question_list(self):
        return json.loads(self.question_ids)

    def get_answers_dict(self):
        return json.loads(self.user_answers)

    def __str__(self):
        return f"Session for {self.user.username} - {self.subcategory.name if self.subcategory else 'AI'}"