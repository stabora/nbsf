# -*- coding: utf-8 -*-

import os
import MySQLdb
from ConfigParser import SafeConfigParser

class Db:

    baseDir = os.path.dirname(os.path.dirname(__file__))
    config = SafeConfigParser()
    config.read(os.path.join(baseDir, 'config.ini'))

    db = MySQLdb.connect(
        host='localhost',
        user=config.get('mysql_nbsf', 'user'),
        passwd=config.get('mysql_nbsf', 'password'),
        db=config.get('mysql_nbsf', 'db')
    )

    cursor = db.cursor()

    def __del__(self):
        self.db.close()

    @staticmethod
    def guardar_consulta(**kwargs):
        Db.cursor.execute(
            'INSERT INTO consultas (consulta, tx, rx, ip) VALUES (%s, %s, %s, %s)',
            (
                kwargs['consulta'],
                kwargs['tx'],
                kwargs['rx'],
                kwargs['ip']
            )
        )

        Db.db.commit()
