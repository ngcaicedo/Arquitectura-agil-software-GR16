import requests

def suspectUser(user):
    profile = get_user_profile(user)
    return profile != "ventas"

def get_user_profile(email):
    response = requests.get(f'http://usuarios:5001/users/{email}')
    if response.status_code == 200:
        return response.json().get('perfil')
    return None