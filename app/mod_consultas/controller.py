# -*- coding: utf-8 -*-

from flask import Response, render_template, request, redirect, url_for
from lxml import etree
from suds.client import Client
from suds.sudsobject import asdict
from app import app
from app.helpers.util import Util
from app.helpers.db import Db
from app.helpers.xml import XML
from app.helpers.html import HTML
from app.helpers.mensajeria import Mensajeria

params = None


@app.before_request
def init():
    global params
    params = request.form if request.method == 'POST' else request.args


@app.route('/consultarPadronForm')
def consultarPadronForm():
    return render_template('consultas/padronElectoral_form.html')


@app.route('/consultarPadron', methods=['GET', 'POST'])
def consultarPadron():
    if not params:
        return redirect(url_for('consultarPadronForm'))

    numeroDocumento = params.get('numeroDocumento')
    formato = params.get('formato')
    xml_ped = XML.get_xml_consultarPadron(numeroDocumento)
    entorno = params.get('entorno', 'DESARROLLO')

    response, msg = Util.get_http_request(
        app.config['MENSAJERIA_HOST_' + entorno] + app.config['MENSAJERIA_RESOURCE'],
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

        if formato == 'html':
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

    numeroCliente = params.get('numeroCliente')
    formato = params.get('formato')
    entorno = params.get('entorno', 'DESARROLLO')

    response, xml_ped, msg = Mensajeria.cliConsBlqDesblq(1, numeroCliente, entorno=entorno)

    if response.status_code == 200:
        response = Util.format_replaceXMLEntities(response.content)

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=xml_ped,
            rx=response,
            ip=request.remote_addr
        )

        if formato == 'html':
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

    uidPrestamo = params.get('uidPrestamo')

    response, msg = HTML.get_html_respuestaCuotaMA(uidPrestamo)

    if response:
        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx='UID: ' + uidPrestamo,
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

    numeroCuit = params.get('numeroCuit')
    formato = params.get('formato')
    xml_ped = XML.get_xml_broker_consultarCupoCUAD(numeroCuit)

    response, msg = Util.get_http_request(
        app.config['BROKERWS_HOST'] + app.config['BROKERWS_RESOURCE'],
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

        if formato == 'html':
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
        numeroDocumento = params.get('numeroDocumento')
        nombre = params.get('nombre')
        sexo = params.get('sexo')
        par_xml = XML.get_xml_consultarVeraz(nombre, sexo, numeroDocumento)
    else:
        xml = etree.fromstring(par_xml)
        numeroDocumento = xml.findtext('.//documento')
        nombre = xml.findtext('.//nombre')
        sexo = xml.findtext('.//sexo')

    if debug:
        response = XML.get_xml_respuestaVerazDebug(nombre, sexo, numeroDocumento)
    else:
        response, msg = Util.get_http_request(
            app.config['VERAZ_HOST'] + app.config['VERAZ_RESOURCE'],
            {'par_xml': par_xml},
            use_proxy=True
        )

        if response.status_code == 200:
            response = response.content

            Db.guardar_consulta(
                consulta=str(request.url_rule)[1:],
                tx=par_xml,
                rx=response,
                ip=request.remote_addr
            )
        else:
            return render_template('error.html', texto_error=msg)

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

    numeroTarjeta = params.get('numeroTarjeta')
    formato = params.get('formato')

    try:
        ws = Client(app.config['SOAT_HOST'] + app.config['SOAT_WSDL'])

        ped = ws.factory.create('ConsultaEstadoTarjeta')
        ped.idEntidad = app.config['SOAT_ENTIDAD']
        ped.canal = app.config['SOAT_CANAL']
        ped.ip = app.config['SOAT_IP']
        ped.usuario = app.config['SOAT_USER']
        ped.numeroTarjeta = numeroTarjeta

        ws.service.ConsultaEstadoTarjeta(**asdict(ped))

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
                title=u'Consultar estado de tarjeta de débito',
                variables=HTML.get_html_respuestaOperacionSoat(response)
            )
        else:
            return Response(response, mimetype='text/xml')
    except Exception, e:
        msg = 'Error al realizar la consulta - Motivo: ' + str(e)
        return render_template('error.html', texto_error=msg)


@app.route('/consultarApiPrietoForm', methods=['GET', 'POST'])
def consultarApiPrietoForm():
    return render_template('consultas/apiPrieto_form.html')


@app.route('/consultarApiPrieto', methods=['GET', 'POST'])
def consultarApiPrieto():
    if not params:
        return redirect(url_for('consultarApiPrietoForm'))

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
        app.config['PRIETO_HOST'] + app.config['PRIETO_RESOURCE'],
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

    formato = params.get('formato')
    numeroCliente = params.get('numeroCliente')

    url = app.config['LEGAJO_DIGITAL_HOST'] + app.config['LEGAJO_DIGITAL_WSDL']

    try:
        ws = Client(url)
    except Exception, e:
        msg = 'Error al realizar la consulta - Motivo: ' + str(e)
        return render_template('error.html', texto_error=msg)

    header = ws.factory.create('SecuredWebServiceHeader')
    header.Username = app.config['LEGAJO_DIGITAL_USER']
    header.Password = app.config['LEGAJO_DIGITAL_PASSWORD']

    cliente = ws.factory.create('GetCliente')
    cliente.nroCliente = numeroCliente

    ws.set_options(soapheaders=header)
    ws.service.GetCliente(cliente)

    response = Util.format_removeXMLPrefixes(str(ws.last_received()))

    # DEBUG
    # response = Util.format_removeXMLPrefixes(open(app.config['BASE_DIR'] + '/app/tests/legajoDigital_respuesta.xml').read())

    Db.guardar_consulta(
        consulta=str(request.url_rule)[1:],
        tx=str(ws.last_sent()),
        rx=response,
        ip=request.remote_addr
    )

    if formato == 'html':
        return render_template('consultas/legajoDigital_respuesta.html', variables=HTML.get_html_respuestaLegajoDigital(response))
    else:
        return Response(response, mimetype='text/xml')
