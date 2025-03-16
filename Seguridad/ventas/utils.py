import requests
import random

def suspectUser():
    users = requests.get("http://usuarios/users").json()
    if random.random() < 0.5:
        suspectUsers = []
        for user in users:
            if user.get("perfil") != "ventas":
                suspectUsers.append(user)
        return random.choice(suspectUser)
    return None

