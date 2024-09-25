from django.db import models

class Chat(models.Model):
    username = models.CharField(max_length=100, unique=True)
    token = models.IntegerField(default=0)
    def __str__(self):
        return f'{self.username}, {self.token}'
