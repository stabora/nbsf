
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
from app.helpers.sudslogger import SudsLogger

params = None


@app.before_request
def init():
    global params
    params = request.form if request.method == 'POST' else request.args


@app.errorhandler(Exception)
def handle_errore(e):
    return Response(XML.get_xml_error(e.message), mimetype='text/xml')


@app.route('/consultarPadronForm')
def consultarPadronForm():
    return render_template('consultas/padronElectoral_form.html')


@app.route('/consultarPadron', methods=['POST', 'GET'])
def consultarPadron():
    if not params:
        return redirect(url_for('consultarPadronForm'))
    else:
        Util.check_parameters(['numeroDocumento'], params)

    xml_ped = XML.get_xml_consultarPadron(params.get('numeroDocumento'))

    response, msg = Util.get_http_request(
        '{}{}'.format(
            app.config['MENSAJERIA_HOST_{}'.format(params.get('entorno', 'DESARROLLO').upper())],
            app.config['MENSAJERIA_RESOURCE']
        ),
        {'Consulta': xml_ped},
        trust_env=False
    )

    if response.status_code == 200:
        response = Util.format_replaceXMLEntities(response.content)

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=xml_ped,
            rx=response,
            ip=request.remote_addr
        )

        if params.get('formato') == 'html':
            return render_template('consultas/padronElectoral_respuesta.html', variables=HTML.get_html_respuestaPadronElectoral(response))
        else:
            return Response(response, mimetype="text/xml")
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/consultarClienteForm')
def consultarClienteForm():
    return render_template('consultas/datosCliente_form.html')


@app.route('/consultarCliente', methods=['GET', 'POST'])
def consultarCliente():
    if not params:
        return redirect(url_for('consultarClienteForm'))
    else:
        Util.check_parameters(['numeroCliente'], params)

    response, xml_ped, msg = Mensajeria.cliConsBlqDesblq(1, params.get('numeroCliente'), entorno=params.get('entorno', 'DESARROLLO').upper())

    if response.status_code == 200:
        response = Util.format_replaceXMLEntities(response.content)

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=xml_ped,
            rx=response,
            ip=request.remote_addr
        )

        if params.get('formato') == 'html':
            return render_template('consultas/datosCliente_respuesta.html', variables=HTML.get_html_respuestaDatosCliente(response))
        else:
            return Response(response, mimetype='text/xml')
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/consultarCuotaMAForm')
def consultarCuotaMAForm():
    return render_template('consultas/cuotaMA_form.html')


@app.route('/consultarCuotaMA', methods=['GET', 'POST'])
def consultarCuotaMA():
    if not params:
        return redirect(url_for('consultarCuotaMAForm'))
    else:
        Util.check_parameters(['uidPrestamo'], params)

    response, msg = HTML.get_html_respuestaCuotaMA(params.get('uidPrestamo'))

    if response:
        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx='UID: {}'.format(params.get('uidPrestamo')),
            rx=str(response),
            ip=request.remote_addr
        )

        return render_template('consultas/cuotaMA_respuesta.html', variables=response)
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/consultarCupoCUADForm')
def consultarCupoCUADForm():
    return render_template('consultas/cupoCUAD_form.html')


@app.route('/consultarCupoCUAD', methods=['GET', 'POST'])
def consultarCupoCUAD():
    if not params:
        return redirect(url_for('consultarCupoCUADForm'))
    else:
        Util.check_parameters(['numeroCuit'], params)

    xml_ped = XML.get_xml_broker_consultarCupoCUAD(params.get('numeroCuit'))

    response, msg = Util.get_http_request(
        '{}{}'.format(app.config['BROKERWS_HOST'], app.config['BROKERWS_RESOURCE']),
        {'messageRequest': xml_ped}
    )

    if response.status_code == 200:
        response = Util.format_replaceXMLEntities(response.content[122:-9])

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=xml_ped,
            rx=response,
            ip=request.remote_addr
        )

        if params.get('formato') == 'html':
            return render_template('consultas/cupoCUAD_respuesta.html', variables=HTML.get_html_respuestaCupoCUAD(response))
        else:
            return Response(response, mimetype='text/xml')
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/consultarPrestamosPendientesForm')
def consultarPrestamosPendientesForm():
    return render_template('consultas/prestamosPendientes_form.html')


@app.route('/consultarVerazForm', methods=['GET', 'POST'])
def consultarVerazForm():
    return render_template('consultas/veraz_form.html')


@app.route('/consultarVeraz', methods=['GET', 'POST'])
def consultarVeraz():
    if not params:
        return redirect(url_for('consultarVerazForm'))

    par_xml = params.get('par_xml', '')
    formato = params.get('formato')
    debug = params.get('debug', app.config['VERAZ_DEBUG'])

    if par_xml == '':
        Util.check_parameters(['numeroDocumento', 'nombre', 'sexo'], params)
        numeroDocumento = params.get('numeroDocumento')
        nombre = params.get('nombre')
        sexo = params.get('sexo')
        par_xml = XML.get_xml_consultarVeraz(nombre, sexo, numeroDocumento)
    else:
        xml = etree.fromstring(par_xml)
        numeroDocumento = xml.findtext('.//documento')
        nombre = xml.findtext('.//nombre')
        sexo = xml.findtext('.//sexo')

    if str(debug).upper() == 'TRUE':
        response = XML.get_xml_respuestaVerazDebug(nombre, sexo, numeroDocumento)
    else:
        response, msg = Util.get_http_request(
            '{}{}'.format(app.config['VERAZ_HOST'], app.config['VERAZ_RESOURCE']),
            {'par_xml': par_xml},
            use_proxy=True
        )

        if response.status_code == 200:
            response = response.content
            response = response.decode('iso-8859-1', 'ignore')
        else:
            return render_template('error.html', texto_error=msg)

    Db.guardar_consulta(
        consulta=str(request.url_rule)[1:],
        tx=par_xml,
        rx=response,
        ip=request.remote_addr
    )

    if formato == 'html':
        return render_template('consultas/veraz_respuesta.html', **HTML.get_html_respuestaVeraz(response))
    else:
        return Response(response, mimetype='text/xml')


@app.route('/consultarTarjetaSOATForm', methods=['GET', 'POST'])
def consultarTarjetaSOATForm():
    return render_template(
        'operaciones/soatOperacionTarjeta_form.html',
        title=u'Consultar estado de tarjeta de débito',
        formAction='consultarTarjetaSOAT'
    )


@app.route('/consultarTarjetaSOAT', methods=['GET', 'POST'])
def consultarTarjetaSOAT():
    if not params:
        return redirect(url_for('consultarTarjetaSOATForm'))
    else:
        Util.check_parameters(['numeroTarjeta'], params)

    try:
        ws_log = SudsLogger()
        ws = Client('{}{}'.format(app.config['SOAT_HOST'], app.config['SOAT_WSDL']), plugins=[ws_log])

        ped = ws.factory.create('ConsultaEstadoTarjeta')
        ped.idEntidad = app.config['SOAT_ENTIDAD']
        ped.canal = app.config['SOAT_CANAL']
        ped.ip = app.config['SOAT_IP']
        ped.usuario = app.config['SOAT_USER']
        ped.numeroTarjeta = params.get('numeroTarjeta')

        response = ws.service.ConsultaEstadoTarjeta(**asdict(ped))

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=str(ws_log.last_sent()),
            rx=str(ws_log.last_received()),
            ip=request.remote_addr
        )

        if params.get('formato') == 'html':
            return render_template(
                'operaciones/soatOperacionTarjeta_respuesta.html',
                title=u'Consultar estado de tarjeta de débito',
                variables=HTML.get_html_respuestaOperacionSoat(response)
            )
        else:
            return Response(Util.format_removeXMLPrefixes(str(ws_log.last_received())), mimetype='text/xml')
    except Exception, e:
        msg = 'Error al realizar la consulta - Motivo: {}'.format(str(e))
        return render_template('error.html', texto_error=msg)


@app.route('/consultarApiPrietoForm', methods=['GET', 'POST'])
def consultarApiPrietoForm():
    return render_template('consultas/apiPrieto_form.html')


@app.route('/consultarApiPrieto', methods=['GET', 'POST'])
def consultarApiPrieto():
    if not params:
        return redirect(url_for('consultarApiPrietoForm'))
    else:
        Util.check_parameters(['doc'], params)

    headers = {
        'Accept': 'application/xml',
        'Prieto-APIKey': app.config['PRIETO_APIKEY']
    }

    payload = {
        'doc': params.get('doc'),
        'page': params.get('page', '1'),
        'limit': params.get('limit', '10')
    }

    response, msg = Util.get_http_request(
        '{}{}'.format(app.config['PRIETO_HOST'], app.config['PRIETO_RESOURCE']),
        payload,
        method='GET',
        headers=headers,
        use_proxy=True,
        use_proxy_auth=True,
    )

    if response.status_code == 200:
        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=response.url,
            rx=response.content,
            ip=request.remote_addr
        )

        return Response(response, mimetype='text/xml')
    else:
        return render_template('error.html', texto_error=msg)


@app.route('/consultarLegajoDigitalForm', methods=['GET', 'POST'])
def consultarLegajoDigitalForm():
    return render_template('consultas/legajoDigital_form.html')


@app.route('/consultarLegajoDigital', methods=['GET', 'POST'])
def consultarLegajoDigital():
    if not params:
        return redirect(url_for('consultarLegajoDigitalForm'))
    else:
        Util.check_parameters(['numeroCliente'], params)

    try:
        url = '{}{}'.format(app.config['LEGAJO_DIGITAL_HOST'], app.config['LEGAJO_DIGITAL_WSDL'])
        ws_log = SudsLogger()
        ws = Client(url, plugins=[ws_log])
    except Exception, e:
        msg = 'Error al realizar la consulta - Motivo: {}'.format(str(e))
        return render_template('error.html', texto_error=msg)

    if params.get('debug', 'FALSE').upper() == 'TRUE':
        xml_test = open('{}/app/tests/legajoDigital_respuesta.xml'.format(app.config['BASE_DIR'])).read()
        response = ws.service.GetCliente(__inject={'reply': xml_test})
    else:
        header = ws.factory.create('SecuredWebServiceHeader')
        header.Username = app.config['LEGAJO_DIGITAL_USER']
        header.Password = app.config['LEGAJO_DIGITAL_PASSWORD']

        ws.set_options(soapheaders=header)

        numeroCliente = params.get('numeroCliente')

        if numeroCliente[0:2] == '10':
            cliente = ws.factory.create('GetClienteByCuit')
            cliente.cuitcuil = numeroCliente[2:]
            response = ws.service.GetClienteByCuit(cliente)
        else:
            cliente = ws.factory.create('GetCliente')
            cliente.nroCliente = numeroCliente
            response = ws.service.GetCliente(cliente)

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=str(ws_log.last_sent()),
            rx=str(ws_log.last_received()),
            ip=request.remote_addr
        )

    if params.get('formato') == 'html':
        return render_template('consultas/legajoDigital_respuesta.html', variables=HTML.get_html_respuestaLegajoDigital(response))
    else:
        return Response(Util.format_removeXMLPrefixes(str(ws_log.last_received())), mimetype='text/xml')
