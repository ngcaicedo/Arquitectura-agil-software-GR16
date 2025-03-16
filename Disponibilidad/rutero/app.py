from flask import Flask, jsonify
import random

app = Flask(__name__)

# Rutas esperadas con nombres
RUTAS_POTENCIALES = ["Ruta A", "Ruta B", "Ruta C"]

@app.route('/rutero/ruta', methods=['GET'])
def obtener_ruta():
    # Simular un fallo con un 10% de probabilidad (para testing)
    if random.random() < 0.1:
        return jsonify({"ruta": "Ruta Incorrecta"})  

    ruta = random.choice(RUTAS_POTENCIALES)  
    return jsonify({"ruta": ruta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  
