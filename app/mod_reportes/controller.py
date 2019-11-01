# -*- coding: utf-8 -*-

from flask import render_template, request
from app import app
from app.helpers.db import Db
from app.helpers.util import Util
from base64 import b64decode
from datetime import datetime, timedelta
import os

try:
    import cx_Oracle
except ImportError:
    pass

params = None


@app.before_request
def init():
    global params
    params = request.form if request.method == 'POST' else request.args


@app.route('/reportes/wf/cuentasQRProcesadas', methods=['GET', 'POST'])
def wf_cuentasQRProcesadas():
    try:
        if not params:
            dias_pasados = 1
            return render_template('reportes/wf_cuentaQRProcesadasForm.html', fecha_desde=(datetime.now() - timedelta(days=dias_pasados)).strftime('%d/%m/%Y'), fecha_hasta=datetime.now().strftime('%d/%m/%Y'))

        Util.check_parameters(['fechaDesde', 'fechaHasta'], params)
        os.environ["NLS_LANG"] = ".UTF8"

        with cx_Oracle.connect(
            '{}/{}@{}/{}'.format(
                app.config['ORACLE_NBSF_WF6_USER'],
                b64decode(app.config['ORACLE_NBSF_WF6_PASSWORD']),
                app.config['ORACLE_NBSF_WF6_HOST'],
                app.config['ORACLE_NBSF_WF6_SID']
            )
        ) as db:
            cursor = db.cursor()
            sql_path = os.path.join(app.root_path, 'sql', 'wf_cuentasQR.sql')

            with open(sql_path, 'r') as sql_file:
                sql = sql_file.read()

            cursor.execute(sql, [params.get('fechaDesde'), params.get('fechaHasta')])
            encabezados = [columna[0] for columna in cursor.description]
            registros = cursor.fetchall()

            Db.guardar_consulta(
                consulta=str(request.url_rule)[1:],
                tx='Fecha desde: {} - Fecha hasta: {}'.format(params.get('fechaDesde'), params.get('fechaHasta')),
                rx='Se recuperaron {} registros'.format(cursor.rowcount),
                ip=request.remote_addr
            )

            return render_template('reportes/mostrarResultados.html', titulo='WF Solicitudes masivas - Cuentas QR procesadas', encabezados=encabezados, resultados=registros)
    except Exception, e:
        return render_template('error.html', texto_error=e.message)


@app.route('/reportes/wf/gestionTramites', methods=['GET', 'POST'])
def wf_gestionTramites():
    try:
        if not params:
            dias_pasados = 1
            return render_template('reportes/wf_gestionTramites.html', fecha_desde=(datetime.now() - timedelta(days=dias_pasados)).strftime('%d/%m/%Y'), fecha_hasta=datetime.now().strftime('%d/%m/%Y'))

        Util.check_parameters(['fechaDesde', 'fechaHasta'], params)
        os.environ["NLS_LANG"] = ".UTF8"

        with cx_Oracle.connect(
            '{}/{}@{}/{}'.format(
                app.config['ORACLE_NBSF_WF6_USER'],
                b64decode(app.config['ORACLE_NBSF_WF6_PASSWORD']),
                app.config['ORACLE_NBSF_WF6_HOST'],
                app.config['ORACLE_NBSF_WF6_SID']
            )
        ) as db:
            cursor = db.cursor()
            sql_path = os.path.join(app.root_path, 'sql', 'wf_gestionTramites.sql')

            with open(sql_path, 'r') as sql_file:
                sql = sql_file.read()

            cursor.execute(sql, [params.get('fechaDesde'), params.get('fechaHasta')])
            encabezados = [columna[0] for columna in cursor.description]
            registros = cursor.fetchall()

            Db.guardar_consulta(
                consulta=str(request.url_rule)[1:],
                tx='Fecha desde: {} - Fecha hasta: {}'.format(params.get('fechaDesde'), params.get('fechaHasta')),
                rx='Se recuperaron {} registros'.format(cursor.rowcount),
                ip=request.remote_addr
            )

            return render_template('reportes/mostrarResultados.html', titulo=u'WF Trámites - Reporte de gestión', encabezados=encabezados, resultados=registros)
    except Exception, e:
        return render_template('error.html', texto_error=e.message)
