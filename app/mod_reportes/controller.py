# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for
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


@app.route('/reportes/cuentasQRProcesadasForm')
def cuentasQRProcesadasForm():
    dias_pasados = 1
    return render_template('reportes/cuentaQRProcesadas_form.html', fecha_desde=(datetime.now() - timedelta(days=dias_pasados)).strftime('%d/%m/%Y'), fecha_hasta=datetime.now().strftime('%d/%m/%Y'))


@app.route('/reportes/cuentasQRProcesadas', methods=['GET', 'POST'])
def cuentasQRProcesadas():
    try:
        if not params:
            return redirect(url_for('cuentasQRProcesadasForm'))

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

            cursor.execute(
                (
                    'SELECT SL."UID", SL.FECHA AS "Fecha", ES.DESCRIPCION AS "Estado", MVABM.DESCRIPCION AS "Resoluci&oacute;n ABM", '
                    'CL.TIPODOC AS "Tipo doc.", CL.NUMERODOC AS "Nro. doc.", CL.NROCUIT AS "CUIT", CL.NOMBRECLIENTE AS "Nombre", '
                    'LPAD(NVL(CL.SUCAGE, 0), 3 ,\'0\') || LPAD(NVL(CL.SUCCON, 0), 3 ,\'0\') AS "Actividad AFIP", PC.SUCURSAL AS "CA Suc.", '
                    'PC.CODIGO_TIPO AS "CA Tipo", PC.CODIGO_PRODUCTO AS "CA Prod.", PC.NUMERO AS "CA Nro.", TO_CHAR(PC.CBU) AS CBU, '
                    'EXTRACTVALUE(XMLTYPE.CREATEXML(CIP.XMLRES), \'//Producto[CodigoSistema=1][CodigoProducto=47][1]/Descripcion\') AS "CC vinculada", '
                    '(SELECT C.DESCRIPCION FROM WF_SOLICITUDESMASIVAS.TBL_CON_X_INST CI '
                    'INNER JOIN WF_SOLICITUDESMASIVAS.TBL_CONSULTAS C ON C.CODIGO = CI.CODIGO_CONSULTA '
                    'WHERE CI."UID" = SL."UID" AND CI.ESTADO = 5 AND ROWNUM = 1 '
                    ') AS "Consultas irregulares" '
                    'FROM WF_SOLICITUDESMASIVAS.TBL_SOLICITUDES SL '
                    'INNER JOIN WF_SOLICITUDESMASIVAS.POLL_INGRESO_SOLICITUDES PI ON PI."UID" = SL."UID" '
                    'INNER JOIN WF_SOLICITUDESMASIVAS.TBL_ESTADOS ES ON ES.CODIGO = SL.CODIGO_ESTADO '
                    'LEFT JOIN WF_SOLICITUDESMASIVAS.TBL_PERSONAS PE ON PE."UID" = SL."UID" '
                    'LEFT JOIN WF_SOLICITUDESMASIVAS.TBL_CLIENTES CL ON CL."UID" = SL."UID" '
                    'LEFT JOIN WF_SOLICITUDESMASIVAS.TBL_PRODUCTOS_CUENTAS PC ON PC."UID" = SL."UID" '
                    'LEFT JOIN WF_SOLICITUDESMASIVAS.TBL_CON_X_INST CIP ON CIP."UID" = SL."UID" AND CIP.CODIGO_CONSULTA = 14 '
                    'LEFT JOIN ( '
                    'SELECT DENSE_RANK() OVER (PARTITION BY MVABM."UID" ORDER BY MVABM.FECHA DESC) AS RNK, MVABM.*, ES.DESCRIPCION '
                    'FROM WF_SOLICITUDESMASIVAS.TBL_MOVIMIENTOS MVABM '
                    'INNER JOIN WF_SOLICITUDESMASIVAS.TBL_ESTADOS ES ON ES.CODIGO = MVABM.CODIGO_ESTADO '
                    'WHERE MVABM.DESCRIPCION_ADICIONAL = \'1020\' '
                    ') MVABM '
                    'ON MVABM."UID" = SL."UID" AND MVABM.RNK = 1 '
                    'WHERE PI.ORIGEN_CODIGO_SISTEMA = 10014 AND MVABM.DESCRIPCION IS NOT NULL AND TRUNC(SL.FECHA) BETWEEN TO_DATE(:FECHA_DESDE, \'DD/MM/YYYY\') AND TO_DATE(:FECHA_HASTA, \'DD/MM/YYYY\') '
                    'ORDER BY PI.FECHA_PROCESO_WF'
                ),
                [params.get('fechaDesde'), params.get('fechaHasta')]
            )

            registros = cursor.fetchall()

            Db.guardar_consulta(
                consulta=str(request.url_rule)[1:],
                tx='Fecha desde: {} - Fecha hasta: {}'.format(params.get('fechaDesde'), params.get('fechaHasta')),
                rx='Se recuperaron {} registros'.format(cursor.rowcount),
                ip=request.remote_addr
            )

            return render_template('reportes/mostrarResultados.html', titulo='WF Solicitudes masivas - Cuentas QR procesadas', encabezados=cursor.description, resultados=registros)
    except Exception, e:
        return render_template('error.html', texto_error=e.message)
