from flask import Flask, jsonify
import requests
from collections import Counter

app = Flask(__name__)


# Simulación del servicio Rutero (3 instancias para el proceso de votación)
RUTEROS = ["http://rutero1:5001", "http://rutero2:5001", "http://rutero3:5001"]

# Servicio de VotingRutero que elige la mejor ruta


@app.route('/voting_rutero/seleccionar_ruta', methods=['GET'])
def seleccionar_ruta():
    rutas = []
    fallos = []

    for i, rutero in enumerate(RUTEROS):
        try:
            response = requests.get(
                '{rutero}/rutero/ruta'.format(rutero=rutero))
            if response.status_code == 200:
                ruta = response.json()["ruta"]
                rutas.append((i, ruta))
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
        return jsonify({'error': 'No se pudo determinar la mejor ruta'})
    
    if not conteo_rutas:
        # No se pudo encontrar porque los 3 microservicios fallaron
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

    return jsonify({'mejor_ruta': mejor_ruta, 'servicios_defectuoso': fallos})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
