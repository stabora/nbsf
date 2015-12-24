from app import db


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    programa = db.Column(db.String)
    tx = db.Column(db.Text)
    rx = db.Column(db.Text)
    ip = db.Column(db.String)
