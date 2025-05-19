from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))
    estado = db.Column(db.String(20), default='Activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.cedula}>'

    def has_role(self, role):
        return self.role == role

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    def to_dict(self):
        return {
            'id': self.id,
            'cedula': self.cedula,
            'nombre': self.nombre,
            'role': self.role,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con el usuario
    user = db.relationship('User', backref=db.backref('activity_logs', lazy=True))
    
    @staticmethod
    def log_activity(user, action, details=None):
        """
        Registra una actividad en el sistema
        
        Args:
            user: Usuario que realiza la acción (objeto User o None para acciones del sistema)
            action: Tipo de acción (create, update, delete, login, etc.)
            details: Detalles adicionales de la acción
        """
        log = ActivityLog(
            user_id=user.id if user else None,
            action=action,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.nombre if self.user else 'Sistema',
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }