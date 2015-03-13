from app import db


class Consulta(db.Model):
    __tablename__ = 'consultas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    consulta = db.Column(db.String)
    tx = db.Column(db.Text)
    rx = db.Column(db.Text)
    ip = db.Column(db.String)
