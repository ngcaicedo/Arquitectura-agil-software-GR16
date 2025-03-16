import requests
import hashlib
import json
import faker
import random


def generate_transaction_hash(transaction):
    # Convertir la transacción en una cadena JSON
    transaction_data = json.dumps(transaction, sort_keys=True)
    # Crear el hash SHA-256 de los datos
    return hashlib.sha256(transaction_data.encode('utf-8')).hexdigest()


def generar_datos_ventas(id, creada=False):
    fake = faker.Faker()
    if creada:
        estado = ["pendiente"]
    else:
        estado = ["pendiente", "aprobada"]
    return {
        "id": id,
        "producto": fake.word(),
        "cantidad": fake.random_int(min=1, max=100),
        "valor": fake.random_int(min=1000, max=100000),
        "vendedor": fake.first_name(),
        "estado": random.choice(estado),
        "checkSum": ""
    }


def suspectUser(user):
    profile = get_user_profile(user)
    return profile != "ventas"


def get_user_profile(email):
    response = requests.get(f'http://usuarios:5001/users/{email}')
    if response.status_code == 200:
        return response.json().get('perfil')
    return None
