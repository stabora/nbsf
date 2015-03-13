# -*- coding: utf-8 -*-

from app import db
from app.mod_consultas.models import Consulta


class Db:

    def __del__(self):
        db.close()

    @staticmethod
    def guardar_consulta(**kwargs):
        con = Consulta(
            consulta=kwargs['consulta'],
            tx=kwargs['tx'],
            rx=kwargs['rx'],
            ip=kwargs['ip']
        )

        db.session.add(con)
        db.session.commit()
