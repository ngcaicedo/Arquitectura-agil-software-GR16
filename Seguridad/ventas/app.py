from flask import Flask, request, jsonify
import requests
from flask_restful import Api, Resource
from utils import suspectUser
from flask_jwt_extended import jwt_required

app = Flask(__name__)
api = Api(app)


ventasListar = [
    {
        "id": 1,
        "producto": "Papa",
        "cantidad": 10,
        "valor": 10000,
        "vendedor": "Jose"
    },
    {
        "id": 2,
        "producto": "Arroz",
        "cantidad": 5,
        "valor": 5000,
        "vendedor": "Jose"
    },
    {
        "id": 3,
        "producto": "Papa",
        "cantidad": 10,
        "valor": 10000,
        "vendedor": "John"
    },
    {
        "id": 4,
        "producto": "Arroz",
        "cantidad": 5,
        "valor": 5000,
        "vendedor": "John"
    }
]

@jwt_required()
class Venta(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        if token:
            # Validación del tipo de usuario
            intruder = suspectUser()
            if intruder:
                return jsonify({"message": "Unauthorized"}), 401
            response = requests.get("http://ventas:5000/listado", headers={"Authorization": token})
            if response.status_code == 200:
                return jsonify({"message": "Venta realizada"})
            return jsonify({"message": "Unauthorized"}), 401
        return jsonify({"message": "Unauthorized"}), 401
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)