# -*- coding: utf-8 -*-

import requests
from flask import Response, render_template, request, redirect, url_for
from lxml import etree
from helpers.xml import XML
from helpers.html import HTML
from helpers.mensajeria import Mensajeria
from app import app
from app.helpers.util import Util
from app.helpers.db import Db

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

    session = requests.Session()

    payload = {
        'Consulta': xml_ped
    }

    response = session.post(
        app.config['NBSF_MENSAJERIA_HOST'] + app.config['NBSF_MENSAJERIA_RESOURCE'],
        data=payload
    )

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


@app.route('/consultarClienteForm')
def consultarClienteForm():
    return render_template('consultas/datosCliente_form.html')


@app.route('/consultarCliente', methods=['GET', 'POST'])
def consultarCliente():
    if not params:
        return redirect(url_for('consultarClienteForm'))

    numeroCliente = params.get('numeroCliente')
    formato = params.get('formato')

    response = Mensajeria.cliConsBlqDesblq(1, numeroCliente)

    if formato == 'html':
        return render_template('consultas/datosCliente_respuesta.html', variables=HTML.get_html_respuestaDatosCliente(response))
    else:
        return Response(response, mimetype='text/xml')


@app.route('/desbloquearClienteForm')
def desbloquearClienteForm():
    return render_template('consultas/desbloquearCliente_form.html')


@app.route('/desbloquearCliente', methods=['GET', 'POST'])
def desbloquearCliente():
    if not params:
        return redirect(url_for('desbloquearClienteForm'))

    numeroCliente = params.get('numeroCliente')
    usuario = params.get('usuario')

    response = Mensajeria.cliConsBlqDesblq(8, numeroCliente, usuario)

    return Response(response, mimetype='text/xml')


@app.route('/consultarCuotaMAForm')
def consultarCuotaMAForm():
    return render_template('consultas/cuotaMA_form.html')


@app.route('/consultarCuotaMA', methods=['GET', 'POST'])
def consultarCuotaMA():
    if not params:
        return redirect(url_for('consultarCuotaMAForm'))

    uidPrestamo = params.get('uidPrestamo')

    response = HTML.get_html_respuestaCuotaMA(uidPrestamo)

    Db.guardar_consulta(
        consulta=str(request.url_rule)[1:],
        tx='UID: ' + uidPrestamo,
        rx=str(response),
        ip=request.remote_addr
    )

    return render_template('consultas/cuotaMA_respuesta.html', variables=response)


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

    session = requests.Session()

    payload = {
        'messageRequest': xml_ped
    }

    response = session.post(
        app.config['NBSF_BROKERWS_HOST'] + app.config['NBSF_BROKERWS_RESOURCE'],
        data=payload
    ).content

    response = Util.format_replaceXMLEntities(response[122:-9])

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


@app.route('/consultarPrestamosPendientesForm')
def consultarPrestamosPendientesForm():
    return render_template('consultas/prestamosPendientes_form.html')


@app.route('/bajaPrestamosForm')
def bajaPrestamosForm():
    return render_template('consultas/bajaPrestamos_form.html')


@app.route('/prestamosPendientes', methods=['GET', 'POST'])
def prestamosPendientes():
    if not params:
        return redirect(url_for('consultarPrestamosPendientesForm'))

    accion = params.get('accion')
    tipoDocumento = params.get('tipoDocumento')
    numeroDocumento = params.get('numeroDocumento')
    uidPrestamo = params.get('uidPrestamo', 0)
    formato = params.get('formato')

    if accion == 'BajaEnWF' and not uidPrestamo:
        return redirect(url_for('bajaMasivaPrestamos'), code=307)

    par_xml = XML.get_xml_broker_consultarPrestamos(accion, tipoDocumento, numeroDocumento, uidPrestamo)

    payload = {
        'messageRequest': par_xml
    }

    session = requests.Session()

    response = session.post(
        app.config['NBSF_BROKERWS_HOST'] + app.config['NBSF_BROKERWS_RESOURCE'],
        data=payload
    ).content

    response = Util.format_replaceXMLEntities(response[122:-9])

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


@app.route('/bajaMasivaPrestamos', methods=['GET', 'POST'])
def bajaMasivaPrestamos():
    if not params:
        return redirect(url_for('/'))

    tipoDocumento = params.get('tipoDocumento')
    numeroDocumento = params.get('numeroDocumento')

    payload = {
        'messageRequest': XML.get_xml_broker_consultarPrestamos('SelectEnWF', tipoDocumento, numeroDocumento)
    }

    session = requests.Session()

    response = session.post(
        app.config['NBSF_BROKERWS_HOST'] + app.config['NBSF_BROKERWS_RESOURCE'],
        data=payload
    ).content

    xml = etree.fromstring(Util.format_replaceXMLEntities(response[122:-9]))

    prestamos = {}

    for prestamo in xml.findall('.//{http://tempuri.org/PrestamosEnWFDS.xsd}NBSF_PrestamosEnWF'):
        idPrestamo = prestamo.findtext('.//{http://tempuri.org/PrestamosEnWFDS.xsd}IDWorkFlow')

        payload = {
            'messageRequest': XML.get_xml_broker_consultarPrestamos('BajaEnWF', tipoDocumento, numeroDocumento, idPrestamo)
        }

        responseBaja = session.post(
            app.config['NBSF_BROKERWS_HOST'] + app.config['NBSF_BROKERWS_RESOURCE'],
            data=payload
        ).content

        xmlBaja = etree.fromstring(Util.format_replaceXMLEntities(responseBaja[122:-9]))

        prestamos[idPrestamo] = xmlBaja.findtext('.//Body/StringData', 'N/D')

    return render_template('consultas/bajaMasivaPrestamos_respuesta.html', prestamos=prestamos)


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

    payload = {
        'par_xml': par_xml
    }

    session = requests.Session()

    if debug:
        response = XML.get_xml_respuestaVerazDebug(nombre, sexo, numeroDocumento)
    else:
        response = session.post(
            app.config['VERAZ_HOST'] + app.config['VERAZ_RESOURCE'],
            data=payload,
            proxies=Util.get_proxies()
        ).content

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
