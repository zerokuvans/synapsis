import mysql.connector

db = mysql.connector()

class Suministro(db.Model):
    __tablename__ = 'suministros'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    unidad_medida = db.Column(db.String(50), nullable=False)
    familia = db.Column(db.String(50), nullable=False)
    cliente = db.Column(db.String(50))
    tipo = db.Column(db.String(50))
    estado = db.Column(db.String(50))
    requiere_serial = db.Column(db.String(10))
    serial = db.Column(db.String(100))
    costo_unitario = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False) 