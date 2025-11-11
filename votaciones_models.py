from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Encuesta(db.Model):
    __tablename__ = 'encuestas'
    id_encuesta = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    tipo_encuesta = db.Column(db.Enum('encuesta', 'votacion'), default='encuesta')
    mostrar_resultados = db.Column(db.Boolean, default=False)
    fecha_inicio_votacion = db.Column(db.DateTime)
    fecha_fin_votacion = db.Column(db.DateTime)

    candidatos = db.relationship('Candidato', backref='encuesta', cascade='all, delete-orphan')
    votos = db.relationship('Voto', backref='encuesta', cascade='all, delete-orphan')


class Candidato(db.Model):
    __tablename__ = 'candidatos'
    id_candidato = db.Column(db.Integer, primary_key=True)
    id_encuesta = db.Column(db.Integer, db.ForeignKey('encuestas.id_encuesta'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    foto_url = db.Column(db.String(500))
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    votos = db.relationship('Voto', backref='candidato', cascade='all, delete-orphan')


class Voto(db.Model):
    __tablename__ = 'votos'
    id_voto = db.Column(db.Integer, primary_key=True)
    id_encuesta = db.Column(db.Integer, db.ForeignKey('encuestas.id_encuesta'), nullable=False)
    id_candidato = db.Column(db.Integer, db.ForeignKey('candidatos.id_candidato'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.idusuarios'), nullable=False)
    fecha_voto = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

    __table_args__ = (
        db.UniqueConstraint('id_encuesta', 'id_usuario', name='uniq_voto'),
    )