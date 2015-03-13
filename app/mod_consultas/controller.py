# -*- coding: utf-8 -*-

import requests
from flask import Response, render_template, request, redirect, url_for
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


@app.route('/consultarPadron', methods=['GET', 'POST'])
def consultarPadron():
    numeroDocumento = params.get('numeroDocumento')
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
def consultarCupoCuad():
    if not params:
        return redirect(url_for('consultarCupoCUADForm'))

    numeroCuit = params.get('numeroCuit')
    formato = params.get('formato')
    xml_ped = XML.get_xml_consultarCupoCUAD(numeroCuit)

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
        return render_template('consultas/cupoCUAD_respuesta.html', variables=HTML.get_html_respuestaCUAD(response))
    else:
        return Response(response, mimetype='text/xml')


@app.route('/consultarVerazForm', methods=['GET', 'POST'])
def consultarVerazForm():
    return render_template('consultas/veraz_form.html')


@app.route('/consultarVeraz', methods=['GET', 'POST'])
def consultarVeraz():
    if not params:
        return redirect(url_for('consultarVerazForm'))

    numeroDocumento = params.get('numeroDocumento')
    nombre = params.get('nombre')
    sexo = params.get('sexo')
    formato = params.get('formato')

    par_xml = XML.get_xml_consultarVeraz(nombre, sexo, numeroDocumento)

    payload = {
        'par_xml': par_xml
    }

    session = requests.Session()

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
