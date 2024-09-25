from django.contrib import admin

from .models import Chat

@admin.register(Chat)
class Chat(admin.ModelAdmin):
    list_display=('username', 'token')