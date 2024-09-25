from rest_framework import serializers

from models.models import Chat
class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = ('__all__')