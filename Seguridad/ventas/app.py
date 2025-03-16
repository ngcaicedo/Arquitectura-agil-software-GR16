from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from utils import suspectUser, get_user_profile

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)
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


class Venta(Resource):

    @jwt_required()
    def get(self):
        # Obtener la identidad del usuario desde el token JWT
        current_user = get_jwt_identity()
        print(f"The current user is {current_user}")
        # Obtener el perfil del usuario
        perfil = get_user_profile(current_user)
        print(f"The current user profile is {perfil}")
        if perfil is None:
            return jsonify({"message": "User profile not found"})
        # Validación del tipo de usuario
        #intruder = suspectUser(current_user)
        if perfil!="ventas":
            return jsonify({"message": "Unauthorized"})
        # Aquí puedes agregar la lógica para manejar la solicitud GET
        return jsonify({"message": "Authorized", "user": current_user, "perfil": perfil})

    @jwt_required()
    def post(self):
        data = request.get_json()
        # Aquí puedes agregar la lógica para manejar la solicitud POST
        return jsonify({"message": "POST request received", "data": data}), 201
    
api.add_resource(Venta, '/ventas')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)