from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from utils import suspectUser, get_user_profile, generate_transaction_hash, generar_datos_ventas

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)
api = Api(app)

ventasListar = [generar_datos_ventas(i, True) for i in range(1, 20)]



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
        # intruder = suspectUser(current_user)
        if perfil != "ventas":
            return jsonify({"message": "Unauthorized"})
        # Aquí puedes agregar la lógica para manejar la solicitud GET
        return jsonify({"message": "Authorized", "user": current_user, "perfil": perfil})

    @jwt_required()
    def put(self, id_venta):
        # Obtener los datos de la solicitud
        data = request.get_json()
        new_check = generate_transaction_hash(data)

        # Buscar la venta con el id_venta proporcionado
        venta = next(
            (venta for venta in ventasListar if venta["id"] == id_venta), None)

        # Si la venta no existe
        if venta is None:
            return jsonify({"message": "Venta no encontrada"})

        # Datos a actualizar
        updated_fields = {
            'producto': data.get('producto'),
            'cantidad': data.get('cantidad'),
            'valor': data.get('valor'),
            'estado': data.get('estado')
        }

        # Lógica para manejar las ventas en diferentes estados
        if venta['checkSum'] == '':
            # Si el checkSum está vacío y el estado no es 'aprobada'
            if data.get('estado') != 'aprobada':
                for key, value in updated_fields.items():
                    venta[key] = value
                return jsonify({"message": "Venta actualizada", "id_venta": venta.get('id')})

            # Si el estado es 'aprobada', asignamos el checkSum
            elif data.get('estado') == 'aprobada':
                for key, value in updated_fields.items():
                    venta[key] = value
                venta["checkSum"] = new_check
                return jsonify({"message": "Venta aprobada", "id_venta": venta.get('id')})

        # Si el checkSum ya existe y no hay cambios
        elif venta['checkSum'] == new_check:
            return jsonify({"message": "Sin cambios", "id_venta": venta.get('id')})

        # Si la venta ya está aprobada, no se puede modificar
        else:
            return jsonify({"message": "No es posible realizar cambios a una venta aprobada", "id_venta": venta.get('id')})


api.add_resource(Venta, '/ventas', '/ventas/<int:id_venta>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
