from flask import Flask, request, jsonify
from datetime import date
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

@app.route('/check_submission', methods=['GET'])
def check_submission():
    user_id = request.args.get('user_id')
    submission_date = request.args.get('date')
    
    # Replace with your actual database query logic
    # Example: Check if a record exists in the database for the given user_id and date
    submission_exists = False  # Replace with actual database check

    # Example database check (pseudo-code):
    # submission_exists = db.session.query(Submission).filter_by(user_id=user_id, date=submission_date).first() is not None

    return jsonify({'submitted': submission_exists})

@app.route('/logistica/guardar_firma', methods=['POST'])
def guardar_firma():
    try:
        # Obtener datos del formulario
        firma = request.form.get('firma')
        id_asignador = request.form.get('id_asignador')
        id_asignacion = request.form.get('id_asignacion')  # Suponiendo que también envías el ID de la asignación

        # Validar que los datos necesarios estén presentes
        if not firma or not id_asignador or not id_asignacion:
            return jsonify({'status': 'error', 'message': 'Datos incompletos'}), 400

        # Buscar la asignación en la base de datos
        asignacion = Asignacion.query.get(id_asignacion)
        if not asignacion:
            return jsonify({'status': 'error', 'message': 'Asignación no encontrada'}), 404

        # Actualizar la asignación con la firma y el ID del asignador
        asignacion.asignacion_firma = firma
        asignacion.id_asignador = id_asignador
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Firma guardada exitosamente'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/logistica/ultima_asignacion', methods=['GET'])
def obtener_ultima_asignacion():
    try:
        # Suponiendo que tienes un modelo Asignacion con un campo de fecha
        ultima_asignacion = Asignacion.query.order_by(Asignacion.fecha.desc()).first()
        if ultima_asignacion:
            return jsonify({'status': 'success', 'id_asignacion': ultima_asignacion.id_asignacion})
        else:
            return jsonify({'status': 'error', 'message': 'No se encontró ninguna asignación'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/logistica/registrar_asignacion_con_firma', methods=['POST'])
def registrar_asignacion_con_firma():
    try:
        # Obtener datos del formulario
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha = request.form.get('fecha')
        cargo = request.form.get('cargo')
        firma = request.form.get('firma')
        id_asignador = request.form.get('id_asignador')

        # Validar datos
        if not all([id_codigo_consumidor, fecha, cargo, firma, id_asignador]):
            return jsonify({'status': 'error', 'message': 'Datos incompletos'}), 400

        # Crear nueva asignación
        nueva_asignacion = Asignacion(
            id_codigo_consumidor=id_codigo_consumidor,
            fecha=fecha,
            cargo=cargo,
            asignacion_firma=firma,
            id_asignador=id_asignador
        )
        db.session.add(nueva_asignacion)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Asignación y firma guardadas correctamente', 'id_asignacion': nueva_asignacion.id_asignacion})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)