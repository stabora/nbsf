# -*- coding: utf-8 -*-

from flask import Response, render_template, request, redirect, url_for
from flask_user import login_required
from lxml import etree
from suds.client import Client
from suds.sudsobject import asdict
from app import app
from app.helpers.util import Util
from app.helpers.db import Db
from app.helpers.html import HTML
from app.helpers.xml import XML
from app.helpers.mensajeria import Mensajeria
from app.helpers.sudslogger import SudsLogger

params = None


@app.before_request
def init():
    global params
    params = request.form if request.method == 'POST' else request.args


@app.route('/operaciones/as400/gestionarBloqueoCliente', methods=['GET', 'POST'])
@login_required
def as400_gestionarBloqueoCliente():
    if not params:
        return render_template('operaciones/as400_gestionarBloqueoClienteForm.html')
    else:
        Util.check_parameters(['numeroCliente', 'usuario', 'operacion'], params)

    response, xml_ped, msg = Mensajeria.cliConsBlqDesblq(
        params.get('operacion'),
        params.get('numeroCliente'),
        params.get('usuario'),
        params.get('entorno', 'DESARROLLO')
    )

    if response.status_code == 200:
        response = Util.format_replaceXMLEntities(response.content)

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=xml_ped,
            rx=response,
            ip=request.remote_addr
        )

        return Response(response, mimetype='text/xml')
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/operaciones/broker/gestionarPrestamos', methods=['GET', 'POST'])
@login_required
def broker_gestionarPrestamos():
    if not params:
        return render_template('operaciones/broker_operacionPrestamosForm.html')
    else:
        Util.check_parameters(['tipoDocumento', 'numeroDocumento', 'accion'], params)

    if params.get('accion') == 'BajaEnWF' and not params.get('uidPrestamo', 0):
        return redirect(url_for('broker_bajaMasivaPrestamos', tipoDocumento=params.get('tipoDocumento'), numeroDocumento=params.get('numeroDocumento')), code=307)

    par_xml = XML.get_xml_broker_consultarPrestamos(
        params.get('accion'),
        params.get('tipoDocumento'),
        params.get('numeroDocumento'),
        params.get('uidPrestamo', 0)
    )

    response, msg = Util.get_http_request(
        '{}{}'.format(app.config['BROKERWS_HOST'], app.config['BROKERWS_RESOURCE']),
        {'messageRequest': par_xml}
    )

    if response.status_code == 200:
        response = Util.format_replaceXMLEntities(response.content[122:-9])

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=par_xml,
            rx=response,
            ip=request.remote_addr
        )

        if params.get('formato') == 'html':
            return render_template('consultas/broker_prestamosPendientes.html', variables=HTML.get_html_respuestaPrestamosPendientes(response))
        else:
            return Response(response, mimetype="text/xml")
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/operaciones/broker/bajaMasivaPrestamos', methods=['GET', 'POST'])
@login_required
def broker_bajaMasivaPrestamos():
    if not params:
        return redirect(url_for('broker_gestionarPrestamosForm'))
    else:
        Util.check_parameters(['tipoDocumento', 'numeroDocumento'], params)

    response, msg = Util.get_http_request(
        '{}{}'.format(app.config['BROKERWS_HOST'], app.config['BROKERWS_RESOURCE']),
        {'messageRequest': XML.get_xml_broker_consultarPrestamos('SelectEnWF', params.get('tipoDocumento'), params.get('numeroDocumento'))}
    )

    if response.status_code == 200:
        xml = etree.fromstring(Util.format_replaceXMLEntities(response.content[122:-9]))
        prestamos = {}
        namespaces = {'ns': app.config['BROKERWS_XMLNS_PRESTAMOS']}

        for prestamo in xml.findall('.//ns:NBSF_PrestamosEnWF', namespaces=namespaces):
            idPrestamo = prestamo.findtext('.//ns:IDWorkFlow', namespaces=namespaces)

            responseBaja, msgBaja = Util.get_http_request(
                '{}{}'.format(app.config['BROKERWS_HOST'], app.config['BROKERWS_RESOURCE']),
                {'messageRequest': XML.get_xml_broker_consultarPrestamos('BajaEnWF', params.get('tipoDocumento'), params.get('numeroDocumento'), idPrestamo)}
            )

            if response.status_code == 200:
                xmlBaja = etree.fromstring(Util.format_replaceXMLEntities(responseBaja.content[122:-9]))
                prestamos[idPrestamo] = xmlBaja.findtext('.//Body/StringData', 'N/D')
            else:
                prestamos[idPrestamo] = msgBaja

        return render_template('operaciones/broker_bajaMasivaPrestamos.html', prestamos=prestamos)
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/operaciones/soat/habilitarTarjeta', methods=['GET', 'POST'])
@login_required
def soat_habilitarTarjeta():
    if not params:
        return render_template(
            'operaciones/soat_habilitarTarjetaForm.html',
            title=u'Habilitar tarjeta de débito',
            formAction='soat_habilitarTarjeta'
        )
    else:
        Util.check_parameters(['numeroTarjeta'], params)

    try:
        ws_log = SudsLogger()
        ws = Client('{}{}'.format(app.config['SOAT_HOST'], app.config['SOAT_WSDL']), plugins=[ws_log])

        ped = ws.factory.create('HabilitacionDeTarjeta')
        ped.idEntidad = app.config['SOAT_ENTIDAD']
        ped.canal = app.config['SOAT_CANAL']
        ped.ip = app.config['SOAT_IP']
        ped.usuario = app.config['SOAT_USER']
        ped.numeroTarjeta = params.get('numeroTarjeta').replace('-', '')

        response = ws.service.HabilitacionDeTarjeta(**asdict(ped))

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=str(ws_log.last_sent()),
            rx=str(ws_log.last_received()),
            ip=request.remote_addr
        )

        if params.get('formato') == 'html':
            return render_template(
                'operaciones/soat_habilitarTarjeta.html',
                title=u'Habilitar tarjeta de débito',
                variables=HTML.get_html_respuestaOperacionSoat(response)
            )
        else:
            return Response(Util.format_removeXMLPrefixes(str(ws_log.last_received())), mimetype='text/xml')
    except Exception, e:
        msg = 'Error al realizar la consulta - Motivo: {}'.format(str(e))
        return render_template('error.html', texto_error=msg)
