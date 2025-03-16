import requests
from ventas.utils import generate_transaction_hash, generar_datos_ventas
from validacion_auth import login_user
import json
import random
from datetime import datetime


def log(id, date, id_venta, estado, mensaje):
    """Registra logs en formato JSON para análisis estadístico."""
    log_entry = {
        "timestamp": date,
        "id_venta": id_venta,
        "estado": estado,
        "mensaje": mensaje

    }
    with open('valida_modificacion_venta.csv', 'a+') as f:
        f.write('{id}\t{fecha}\t{id_venta}\t{estado}\t{mensaje}'.format(id=id, fecha=datetime.now(
        ).isoformat(), id_venta=log_entry.get('id_venta'), estado=log_entry.get('estado'), mensaje=log_entry.get('mensaje')) + '\n')
    return f'Logged message: {json.dumps(log_entry)}'


def validar_venta(id,date):
    login, data_user = login_user()
    token = login.get("token")
    ids = list(range(1, 20))
    url = f"http://localhost/ventas/{random.choice(ids)}"
    headers = {
        "Authorization": "Bearer " + token
    }
    data = generar_datos_ventas(random.choice(ids))
    response = requests.put(url, headers=headers, json=data)
    response = response.json()
    log(id, date, response.get('id_venta'), data.get("estado"), response.get('message'))
    print(response, date)


for i in range(100):
    date = datetime.now().isoformat()
    validar_venta(i, date)
