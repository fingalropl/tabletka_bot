from django.db import models

# class Chat(models.Model):
#     username = models.CharField(max_length=100, unique=True)    
#     def __str__(self):
#         return f'{self.username}'

class Reminder(models.Model):
    chat = models.IntegerField()
    day = models.IntegerField(default=10)
    hour = models.IntegerField()
    minute = models.IntegerField()
    med = models.CharField(max_length=100)
    add = models.CharField(max_length=100)