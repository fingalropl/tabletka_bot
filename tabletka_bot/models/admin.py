from django.contrib import admin

from .models import Reminder

# @admin.register(Chat)
# class Chat(admin.ModelAdmin):
#     list_display=('username',)

@admin.register(Reminder)
class Reminder(admin.ModelAdmin):
    list_display=('chat',)