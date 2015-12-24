# -*- coding: utf-8 -*-

from flask import Response, render_template, request, redirect, url_for
from lxml import etree
from suds.client import Client
from suds.sudsobject import asdict
from app import app
from app.helpers.util import Util
from app.helpers.db import Db
from app.helpers.html import HTML
from app.helpers.xml import XML
from app.helpers.mensajeria import Mensajeria

params = None


@app.before_request
def init():
    global params
    params = request.form if request.method == 'POST' else request.args


@app.route('/as400BloqueoClienteForm')
def as400BloqueoClienteForm():
    return render_template('operaciones/as400BloqueoCliente_form.html')


@app.route('/as400BloqueoCliente', methods=['GET', 'POST'])
def as400BloqueoCliente():
    if not params:
        return redirect(url_for('as400BloqueoClienteForm'))

    numeroCliente = params.get('numeroCliente')
    usuario = params.get('usuario')
    operacion = params.get('operacion')
    entorno = params.get('entorno', 'DESARROLLO')

    response, xml_ped, msg = Mensajeria.cliConsBlqDesblq(operacion, numeroCliente, usuario, entorno)

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


@app.route('/brokerOperacionPrestamosForm')
def brokerOperacionPrestamosForm():
    return render_template('operaciones/brokerOperacionPrestamos_form.html')


@app.route('/brokerOperacionPrestamos', methods=['GET', 'POST'])
def brokerOperacionPrestamos():
    if not params:
        return redirect(url_for('brokerOperacionPrestamosForm'))

    accion = params.get('accion')
    tipoDocumento = params.get('tipoDocumento')
    numeroDocumento = params.get('numeroDocumento')
    uidPrestamo = params.get('uidPrestamo', 0)
    formato = params.get('formato')

    if accion == 'BajaEnWF' and not uidPrestamo:
        return redirect(url_for('brokerBajaMasivaPrestamos'), code=307)

    par_xml = XML.get_xml_broker_consultarPrestamos(accion, tipoDocumento, numeroDocumento, uidPrestamo)

    response, msg = Util.get_http_request(
        app.config['BROKERWS_HOST'] + app.config['BROKERWS_RESOURCE'],
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

        if formato == 'html':
            return render_template('consultas/prestamosPendientes_respuesta.html', variables=HTML.get_html_respuestaPrestamosPendientes(response))
        else:
            return Response(response, mimetype="text/xml")
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/brokerBajaMasivaPrestamos', methods=['GET', 'POST'])
def brokerBajaMasivaPrestamos():
    if not params:
        return redirect(url_for('brokerOperacionPrestamosForm'))

    tipoDocumento = params.get('tipoDocumento')
    numeroDocumento = params.get('numeroDocumento')

    response, msg = Util.get_http_request(
        app.config['BROKERWS_HOST'] + app.config['BROKERWS_RESOURCE'],
        {'messageRequest': XML.get_xml_broker_consultarPrestamos('SelectEnWF', tipoDocumento, numeroDocumento)}
    )

    if response.status_code == 200:
        xml = etree.fromstring(Util.format_replaceXMLEntities(response.content[122:-9]))
        prestamos = {}
        namespaces = {'ns': app.config['BROKERWS_XMLNS_PRESTAMOS']}

        for prestamo in xml.findall('.//ns:NBSF_PrestamosEnWF', namespaces=namespaces):
            idPrestamo = prestamo.findtext('.//ns:IDWorkFlow', namespaces=namespaces)

            responseBaja, msgBaja = Util.get_http_request(
                app.config['BROKERWS_HOST'] + app.config['BROKERWS_RESOURCE'],
                {'messageRequest': XML.get_xml_broker_consultarPrestamos('BajaEnWF', tipoDocumento, numeroDocumento, idPrestamo)}
            )

            if response.status_code == 200:
                xmlBaja = etree.fromstring(Util.format_replaceXMLEntities(responseBaja.content[122:-9]))
                prestamos[idPrestamo] = xmlBaja.findtext('.//Body/StringData', 'N/D')
            else:
                prestamos[idPrestamo] = msgBaja

        return render_template('operaciones/brokerBajaMasivaPrestamos_respuesta.html', prestamos=prestamos)
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/soatHabilitarTarjetaForm', methods=['GET', 'POST'])
def soatHabilitarTarjetaForm():
    return render_template(
        'operaciones/soatOperacionTarjeta_form.html',
        title=u'Habilitar tarjeta de débito',
        formAction='soatHabilitarTarjeta'
    )


@app.route('/soatHabilitarTarjeta', methods=['GET', 'POST'])
def soatHabilitarTarjeta():
    if not params:
        return redirect(url_for('soatHabilitarTarjetaForm'))

    numeroTarjeta = params.get('numeroTarjeta')
    formato = params.get('formato')

    try:
        ws = Client(app.config['SOAT_HOST'] + app.config['SOAT_WSDL'])

        ped = ws.factory.create('HabilitacionDeTarjeta')
        ped.idEntidad = app.config['SOAT_ENTIDAD']
        ped.canal = app.config['SOAT_CANAL']
        ped.ip = app.config['SOAT_IP']
        ped.usuario = app.config['SOAT_USER']
        ped.numeroTarjeta = numeroTarjeta

        ws.service.HabilitacionDeTarjeta(**asdict(ped))

        response = Util.format_removeXMLPrefixes(str(ws.last_received()))

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=ws.last_sent(),
            rx=ws.last_received(),
            ip=request.remote_addr
        )

        if formato == 'html':
            return render_template(
                'operaciones/soatOperacionTarjeta_respuesta.html',
                title=u'Habilitar tarjeta de débito',
                variables=HTML.get_html_respuestaOperacionSoat(response)
            )
        else:
            return Response(response, mimetype='text/xml')
    except Exception, e:
        msg = 'Error al realizar la consulta - Motivo: ' + str(e)
        return render_template('error.html', texto_error=msg)