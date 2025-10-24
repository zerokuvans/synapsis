from flask import Flask, jsonify, request
from flask_login import LoginManager, UserMixin, login_required, current_user

app = Flask(__name__)
app.secret_key = 'test-secret-key'

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.unauthorized_handler
def unauthorized():
    print(f"DEBUG unauthorized_handler: request.path = {request.path}")
    # Devolver JSON para endpoints de API
    api_endpoints = ['/api/', '/preoperacional', '/test_auth']
    if any(request.path.startswith(endpoint) for endpoint in api_endpoints):
        print("DEBUG: Devolviendo JSON 401")
        return jsonify({'error': 'No autorizado', 'message': 'Debe iniciar sesión'}), 401
    else:
        print("DEBUG: Redirigiendo a login")
        return jsonify({'error': 'Redirigir a login'}), 302

class User(UserMixin):
    def __init__(self, id, nombre, role):
        self.id = id
        self.nombre = nombre
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    # Para pruebas, devolver None (usuario no autenticado)
    return None

@app.route('/test_simple', methods=['GET'])
def test_simple():
    return jsonify({'message': 'Endpoint simple funcionando'})

@app.route('/test_auth', methods=['GET'])
@login_required
def test_auth():
    return jsonify({'message': 'Autenticado correctamente', 'user': current_user.id})

@app.route('/preoperacional', methods=['POST'])
@login_required
def preoperacional():
    return jsonify({'message': 'Preoperacional OK'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)