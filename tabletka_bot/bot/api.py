# import json
# import requests
# BASE_URL = 'http://127.0.0.1:8000/api/reminder/'

# def api_create_remind(username,k,drug_name,times,intruction):
#     if k == 'everyday':
#         for i in times:
#             time_parts = i.split(':')   #делаем время на часы и минуты
#             hour = int(time_parts[0]) 
#             minute = int(time_parts[1])
#             requests.post(f'{BASE_URL}', json={"chat":f"{username}",'hour':f'{hour}','minute':f'{minute}','med':f'{drug_name}','add':f'{intruction}'}) #добавляем в БД напоминалку
#             print(f'{username} отправил в Бд напоминалку')
#             response = (requests.get(f'{BASE_URL}?chat={username}')).json() #берем ее обратно, но уже с id
#             id_last_user_remind = (response[-1]).get('id') #берем ток id
#             return hour,minute,id_last_user_remind
# # # api_create_remind(123,'everyday','Виферон',['00:00'],'Ректально')