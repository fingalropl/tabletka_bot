from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
# from rest_framework import filters
# from rest_framework import generics

# import django_filters.rest_framework
# from rest_framework import generics
from .serializer import ReminderSerializer
from models.models import Reminder

# class ChatView(APIView):
#     def post(self, request):
#         serializer = ChatSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status.HTTP_201_CREATED)
#         return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
#     def get(self, request):
#         queryset = Chat.objects.all()
#         return Response(queryset.values())
    
# class ReminderListView(generics.ListAPIView):
#     serializer_class = ReminderSerializer
#     def get_queryset(self):
#         queryset = Reminder.objects.all()
#         username = self.request.query_params.get('chat')
#         if username is not None:
#             queryset = queryset.filter(chat=username)
#         return queryset

class ReminderView(APIView):
    def post(self, request):
        serializer = ReminderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        queryset = Reminder.objects.all()
        username = self.request.query_params.get('chat')
        if username is not None:
            queryset = queryset.filter(chat=username)
        return Response(queryset.values())
    
    def delete(self,request):
        queryset = Reminder.objects.all()
        id = self.request.data.get('id')
        if id is not None:
            queryset = queryset.filter(pk=id)
            queryset.delete()
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_404_NOT_FOUND)