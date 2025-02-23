from flask import Flask, jsonify
import requests
from collections import Counter
from datetime import datetime
from celery_config import make_celery


app = Flask(__name__)

celery = make_celery(app)

@celery.task(name='logVoting')
def logVoting(message):
    with open('voting_rutero.log', 'a+') as f:
        f.write(message + '\n')
    return 'Logged message: {message}'.format(message=message)


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

    for i, rutero in enumerate(RUTEROS):
        try:
            response = consultar_rutero.delay(rutero)
            resultado = response.get(timeout=5)  # Esperar la respuesta
            if "ruta" in resultado:
                rutas.append((i, resultado["ruta"]))
            else:
                fallos.append({"rutero": resultado["rutero"], "error": resultado["error"]})
        except Exception as e:
            # no hay conexion con el rutero
            print('Error al conectarse con {rutero}: {e}'.format(
                rutero=rutero, e=e))
    
    rutas_validas = [ruta for _, ruta in rutas if ruta != 'Ruta Incorrecta']
    conteo_rutas = Counter(rutas_validas)

    print(conteo_rutas)
    if len(rutas_validas) == 1:
        pass
    elif(len(conteo_rutas) == len(rutas_validas)):
        # No se puede determinar porque no hay consenso 
        message = 'VotingRutero: ' + str(datetime.now()) + 'No se pudo determinar la mejor ruta - Sin consenso'
        logVoting.delay(message)
        return jsonify({'error': 'No se pudo determinar la mejor ruta'})
    
    if not conteo_rutas:
        # No se pudo encontrar porque los 3 microservicios fallaron
        message = 'VotingRutero: ' + str(datetime.now()) + 'No se pudo determinar la mejor ruta - Internal Error'
        logVoting.delay(message)
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
    message = 'VotingRutero: ' + str(datetime.now()) + ' - ' + mejor_ruta + ' - Servicios fallidos: ' + str(fallos)
    logVoting.delay(message)
    return jsonify({'mejor_ruta': mejor_ruta, 'servicios_defectuoso': fallos})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
