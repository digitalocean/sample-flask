import requests

# define endpoint
GOOGLE_DRIVE_API = 'https://www.googleapis.com/drive/v3/files'

# define headers
headers = {
    'Authorization': 'AIzaSyCILWQQTLv2SYod0uSD6Zu-YJgP5vBzKFU'
}

# send request
response = requests.get(GOOGLE_DRIVE_API, headers=headers)

# print response
print(response.json())