from flask import Flask, request, jsonify
import requests
from flask_restful import Api, Resource


users = [
    {
        "id": 1,
        "name": "John",
        "email": "john@uniandes.edu.co",
        "password": "1234",
        "perfil": "ventas"
    },

    {
        "id": 2,
        "name": "Diego",
        "email": "diego@uniandes.edu.co",
        "password": "5678",
        "perfil": "transporte"
    },

    {
        "id": 3,
        "name": "Jose",
        "email": "jose@uniandes.edu.co",
        "password": "9012",
        "perfil": "ventas"
    },

    {
        "id": 4,
        "name": "Nicolas",
        "email": "nicolas@uniandes.edu.co",
        "password": "3456",
        "perfil": "compras"
    }
]


app = Flask(__name__)
api = Api(app)


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        for user in users:
            if user["email"] == email and user["password"] == password:
                token = requests.get("http://seguridad:5000/jwt")
                return jsonify({"message": "User logged in", "user_id": user.get('id'), "user_perfil": user.get("perfil"), "token": str(token.json().get('access_token'))})
        return jsonify({"message": "User not found"})


api.add_resource(Login, '/login')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
