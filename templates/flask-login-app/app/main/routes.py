from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, ActivityLog
from datetime import datetime, timedelta
import csv
import io

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.username)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'administrativo':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    # Estadísticas para las tarjetas
    total_users = User.query.count()
    active_users = User.query.filter_by(estado='Activo').count()
    total_roles = db.session.query(User.role).distinct().count()
    new_users = User.query.filter(User.created_at >= datetime.now() - timedelta(days=7)).count()
    
    # Datos para los gráficos
    role_stats = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
    role_labels = [role for role, _ in role_stats]
    role_data = [count for _, count in role_stats]
    
    # Datos de actividad
    activity_dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    activity_counts = []
    for date in activity_dates:
        count = ActivityLog.query.filter(
            db.func.date(ActivityLog.timestamp) == date
        ).count()
        activity_counts.append(count)
    
    # Historial de actividad
    activity_log = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    return render_template('modulos/administrativo/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_roles=total_roles,
                         new_users=new_users,
                         role_labels=role_labels,
                         role_data=role_data,
                         activity_labels=activity_dates[::-1],
                         activity_data=activity_counts[::-1],
                         activity_log=activity_log)

@main.route('/admin/buscar_usuarios', methods=['POST'])
@login_required
def buscar_usuarios():
    if current_user.role != 'administrativo':
        return jsonify({'error': 'No autorizado'}), 403
    
    search_query = request.form.get('search_query', '')
    search_type = request.form.get('search_type', 'cedula')
    role = request.form.get('role', '')
    sort = request.form.get('sort', 'cedula')
    
    # Construir query base
    query = User.query
    
    # Aplicar filtros de búsqueda
    if search_query:
        if search_type == 'cedula':
            query = query.filter(User.cedula.ilike(f'%{search_query}%'))
        elif search_type == 'nombre':
            query = query.filter(User.nombre.ilike(f'%{search_query}%'))
        elif search_type == 'codigo':
            query = query.filter(User.codigo.ilike(f'%{search_query}%'))
        elif search_type == 'rol':
            query = query.filter(User.role.ilike(f'%{search_query}%'))
    
    if role:
        query = query.filter(User.role == role)
    
    # Filtros avanzados
    fecha_desde = request.form.get('fecha_desde')
    fecha_hasta = request.form.get('fecha_hasta')
    estado = request.form.get('estado')
    
    if fecha_desde:
        query = query.filter(User.created_at >= fecha_desde)
    if fecha_hasta:
        query = query.filter(User.created_at <= fecha_hasta)
    if estado:
        query = query.filter(User.estado == estado)
    
    # Aplicar ordenamiento
    if sort == 'cedula':
        query = query.order_by(User.cedula)
    elif sort == 'nombre_asc':
        query = query.order_by(User.nombre.asc())
    elif sort == 'nombre_desc':
        query = query.order_by(User.nombre.desc())
    elif sort == 'reciente':
        query = query.order_by(User.created_at.desc())
    elif sort == 'antiguo':
        query = query.order_by(User.created_at.asc())
    
    users = query.all()
    return jsonify([user.to_dict() for user in users])

@main.route('/admin/exportar_usuarios_csv', methods=['POST'])
@login_required
def exportar_usuarios_csv():
    if current_user.role != 'administrativo':
        return jsonify({'error': 'No autorizado'}), 403
    
    # Aplicar los mismos filtros que en la búsqueda
    query = User.query
    # ... (aplicar los mismos filtros que en buscar_usuarios)
    
    users = query.all()
    
    # Crear archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir encabezados
    writer.writerow(['Cédula', 'Nombre', 'Rol', 'Estado', 'Fecha de Creación'])
    
    # Escribir datos
    for user in users:
        writer.writerow([
            user.cedula,
            user.nombre,
            user.role,
            user.estado,
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Preparar respuesta
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@main.route('/admin/estadisticas_usuarios')
@login_required
def estadisticas_usuarios():
    if current_user.role != 'administrativo':
        return jsonify({'error': 'No autorizado'}), 403
    
    # Obtener estadísticas actualizadas
    role_stats = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
    role_labels = [role for role, _ in role_stats]
    role_data = [count for _, count in role_stats]
    
    activity_dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    activity_counts = []
    for date in activity_dates:
        count = ActivityLog.query.filter(
            db.func.date(ActivityLog.timestamp) == date
        ).count()
        activity_counts.append(count)
    
    return jsonify({
        'role_labels': role_labels,
        'role_data': role_data,
        'activity_labels': activity_dates[::-1],
        'activity_data': activity_counts[::-1]
    })

@main.route('/admin/historial_actividad')
@login_required
def historial_actividad():
    if current_user.role != 'administrativo':
        return jsonify({'error': 'No autorizado'}), 403
    
    activity_log = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    return jsonify([{
        'timestamp': log.timestamp.isoformat(),
        'user': log.user.nombre if log.user else 'Sistema',
        'action': log.action,
        'details': log.details
    } for log in activity_log])