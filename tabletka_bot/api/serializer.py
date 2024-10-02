from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from models.models import Reminder
# class ChatSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Chat
#         fields = ('__all__')

class ReminderSerializer(serializers.ModelSerializer):
    # def create(self,data):
    #     datas = self.initial_data.dict()
    #     use = datas.pop('chat')
    #     print(use)
    #     author = Chat.objects.get(username=use)
    #     print(author)
    #     remind = Reminder.objects.create(chat=author, **datas )
    #     print('asd')
    #     return remind
    class Meta:
        model = Reminder
        fields = ('__all__')