from flask import Flask, jsonify
import requests
from collections import Counter
from datetime import datetime
from celery_config import make_celery
import json
import hashlib


app = Flask(__name__)

celery = make_celery(app)


@celery.task(name='logVoting')
def logVoting(message, status='success', hash=1):
    """Registra logs en formato JSON para análisis estadístico."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "ruta": message,
        "hash": hash
    }
    with open('voting_rutero.csv', 'a+') as f:
        f.write('{fecha}\t{message}\t{hash}\t{status}'.format(fecha=datetime.now(
        ).isoformat(), message=message, hash=hash, status=status) + '\n')
    return f'Logged message: {json.dumps(log_entry)}'


# Simulación del servicio Rutero (3 instancias para el proceso de votación)
RUTEROS = ["http://rutero1:5001", "http://rutero2:5001", "http://rutero3:5001"]


@celery.task(name='consultar_rutero')
def consultar_rutero(rutero):
    """ Tarea asíncrona para consultar un rutero """
    try:
        response = requests.get(f"{rutero}/rutero/ruta")
        if response.status_code == 200:
            return {"rutero": rutero, "ruta": response.json()["ruta"]}
    except Exception as e:
        return {"rutero": rutero, "error": str(e)}

# Servicio de VotingRutero que elige la mejor ruta


@app.route('/voting_rutero/seleccionar_ruta', methods=['GET'])
def seleccionar_ruta():
    rutas = []
    fallos = []
    correctos = []

    # for i, rutero in enumerate(RUTEROS):
    #     try:
    #         response = requests.get(
    #             '{rutero}/rutero/ruta'.format(rutero=rutero))
    #         if response.status_code == 200:
    #             ruta = response.json()["ruta"]
    #             rutas.append((i, ruta))
    #     except Exception as e:
    #         # no hay conexion con el rutero
    #         print('Error al conectarse con {rutero}: {e}'.format(
    #             rutero=rutero, e=e))

    hash = hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:5]
    for i, rutero in enumerate(RUTEROS):
        try:
            response = consultar_rutero.delay(rutero)
            resultado = response.get(timeout=5)  # Esperar la respuesta
            if "ruta" in resultado:
                rutas.append((i, resultado["ruta"]))
            else:
                fallos.append(
                    {"rutero": resultado["rutero"], "error": resultado["error"]})
        except Exception as e:
            # no hay conexion con el rutero
            print('Error al conectarse con {rutero}: {e}'.format(
                rutero=rutero, e=e))

    rutas_validas = [ruta for _, ruta in rutas if ruta != 'Ruta Incorrecta']
    conteo_rutas = Counter(rutas_validas)

    print(conteo_rutas)
    if len(rutas_validas) == 1:
        pass
    elif (len(conteo_rutas) == len(rutas_validas)):
        # No se puede determinar porque no hay consenso
        logVoting.delay('No-consenso', hash, 'fail')
        return jsonify({'error': 'No se pudo determinar la mejor ruta'})

    if not conteo_rutas:
        # No se pudo encontrar porque los 3 microservicios fallaron
        logVoting.delay('All', hash, 'fail')
        return jsonify({'error': 'No se pudo determinar la mejor ruta'}), 500

    print(rutas_validas)
    if (len(rutas_validas) == 1):
        # Solo hay una opcion valida
        mejor_ruta = rutas_validas[0]
    else:
        # Se debe elegir la respuesta mas comun
        mejor_ruta = conteo_rutas.most_common(1)[0][0]

    for index, ruta in rutas:
        if ruta != mejor_ruta or ruta == 'Ruta Incorrecta':
            fallos.append({'rutero': 'rutero{index}'.format(
                index=index+1), 'respuesta_defectuosa': ruta})
        else:
            correctos.append({'rutero': 'rutero{index}'.format(
                index=index+1), 'status': 'success'})

    for correcto in correctos:
        logVoting.delay(correcto['rutero'], hash, correcto['status'])

    for fallo in fallos:
        logVoting.delay(fallo['rutero'], hash, 'fail')

    return jsonify({'mejor_ruta': mejor_ruta, 'servicios_defectuoso': fallos})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
