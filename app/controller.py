# -*- coding: utf-8 -*-

import os
import sys
import urlparse
import requests
import logging
import re
from datetime import datetime
from cgi import escape
from ConfigParser import SafeConfigParser
from jinja2 import Environment, FileSystemLoader

if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

from lib.util import Util
from lib.db import Db


class Application:

    baseDir = os.path.dirname(__file__)
    config = SafeConfigParser()
    config.read(os.path.join(baseDir, 'config.ini'))

    def __call__(self, environ, start_response):
        self.init(environ)
        self.logger.info('Iniciado - IP: ' + self.client_ip)
        self.logger.info('Modo: ' + self.method)

        try:
            output = ''

            if self.method in dir(self):
                output = getattr(self, self.method)()
            else:
                self.response_type = 'html'
                template_params = {'base_url': self.config.get('app', 'base_url')}
                output = self.env.get_template('home.html').render(template_params)

        except (KeyError, IndexError) as e:
            self.response_type = 'xml'
            self.logger.error(u'Error: ' + str(e.message))
            output = u'<error><![CDATA[Parámetro requerido: {}]]></error>'.format(e.message)

        except Exception as e:
            self.response_type = 'xml'
            self.logger.error(u'Error: ' + str(e.message))
            output = '<error><![CDATA[Error inesperado: {}]]></error>'.format(e.message)

        self.logger.info('Finalizado\n')
        logging.shutdown()

        start_response(
            '200 OK',
            [('Content-Type', 'text/' + self.response_type + '; charset=' + self.charset)]
        )

        if self.charset == 'utf-8':
            return output.encode('utf-8')
        else:
            return output

    def init(self, environ):
        self.client_ip = self.get_client_ip(environ)
        logDir = os.path.join(self.baseDir, 'log', datetime.today().strftime('%Y'), datetime.today().strftime('%m'))

        if not os.path.exists(logDir):
            os.makedirs(logDir)
            os.chmod(logDir, 0777)

        logging.basicConfig(
            filename=os.path.join(logDir, 'nbsf_' + datetime.today().strftime('%Y%m%d') + '.log'),
            filemode='a',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s (%(name)s): %(message)s',
            datefmt='%d/%m/%Y %I:%M:%S %p'
        )

        self.logger = logging.getLogger('nbsf')
        self.logger.setLevel(logging.INFO)

        self.hostname = environ.get('HTTP_HOST')
        uri = environ.get('REQUEST_URI')
        uri_parsed = urlparse.urlparse(uri)
        uri_parts = uri_parsed.path.strip('/').split('/')

        if len(uri_parts) == 1:
            self.baseUri = '.'
            self.method = uri_parts[0]
        else:
            self.baseUri = uri_parts[0]
            self.method = uri_parts[1]

        if uri_parsed.query:
            self.params = urlparse.parse_qs(uri_parsed.query)
        else:
            self.params = urlparse.parse_qs(environ.get('wsgi.input').read())

        self.proxies = Util.get_proxies()

        self.env = Environment(
            autoescape=True,
            loader=FileSystemLoader(os.path.join(self.baseDir, 'templates'))
        )

        self.response_type = 'html'
        self.charset = 'utf-8'

    def get_client_ip(self, environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR']
        except KeyError:
            return environ['REMOTE_ADDR']

    def consultarVerazForm(self):
        self.response_type = 'html'
        template_params = {'base_url': self.config.get('app', 'base_url')}

        return self.env.get_template('veraz_form.html').render(template_params)

    def consultarVeraz(self):
        if not self.params:
            return self.consultarVerazForm()

        numeroDocumento = escape(str(self.params['numeroDocumento'][0]))
        nombre = escape(str(self.params['nombre'][0]))
        sexo = self.params['sexo'][0]
        self.response_type = self.params.get('formato', 'xml')[0]
        self.response_type = self.response_type if self.response_type in ('xml', 'html') else 'xml'

        if self.response_type == 'xml':
            self.charset = 'iso-8859-1'

        par_xml = Util.get_xml_consultarVeraz(nombre, sexo, numeroDocumento)

        self.logger.info('Params: ' + str(self.params))
        self.logger.info('Tx: ' + par_xml)

        payload = {
            'par_xml': par_xml
        }

        session = requests.Session()

        response = session.post(
            self.config.get('veraz', 'host') + self.config.get('veraz', 'resource'),
            data=payload,
            proxies=self.proxies
        )

        output = response.content if self.response_type == 'xml' else Util.get_html_respuestaVeraz(self.env, response.content)

        self.logger.info('Rx: ' + re.sub('\s*\n\s*', '', output))

        Db.guardar_consulta(
            consulta=self.method,
            tx=par_xml,
            rx=output,
            ip=self.client_ip
        )

        return output

    def consultarPadron(self):
        self.response_type = 'xml'

        numeroDocumento = escape(str(self.params['numeroDocumento'][0]))
        xml_ped = Util.get_xml_consultarPadron(numeroDocumento)

        session = requests.Session()

        payload = {
            'Consulta': xml_ped
        }

        self.logger.info('Params: ' + str(self.params))
        self.logger.info('Tx: ' + xml_ped)

        response = session.post(
            self.config.get('nbsf_mensajeria', 'host') + self.config.get('nbsf_mensajeria', 'resource'),
            data=payload
        )

        output = Util.format_replaceXMLEntities(response.content)
        self.logger.info('Rx: ' + re.sub('\s*\n\s*', '', output))

        Db.guardar_consulta(
            consulta=self.method,
            tx=xml_ped,
            rx=output,
            ip=self.client_ip
        )

        return output

    def consultarClienteForm(self):
        self.response_type = 'html'
        template_params = {'base_url': self.config.get('app', 'base_url')}

        return self.env.get_template('consultarCliente_form.html').render(template_params)

    def consultarCliente(self):
        if not self.params:
            return self.consultarClienteForm()

        return self.cliConsBlqDesblq(1)  # 1 = Consulta

    def desbloquearClienteForm(self):
        template_params = {'base_url': self.config.get('app', 'base_url')}

        return self.env.get_template('desbloquearCliente_form.html').render(template_params)

    def desbloquearCliente(self):
        if not self.params:
            return self.desbloquearClienteForm()

        return self.cliConsBlqDesblq(8).decode('utf-8')  # 8 = Desbloqueo rechazado

    def consultarCupoCUADForm(self):
        self.response_type = 'html'
        template_params = {'base_url': self.config.get('app', 'base_url')}

        return self.env.get_template('cuad_form.html').render(template_params)

    def consultarCupoCUAD(self):
        if not self.params:
            return self.consultarCupoCUADForm()

        numeroCuit = escape(str(self.params['numeroCuit'][0]))
        self.response_type = self.params.get('formato', 'xml')[0]
        self.response_type = self.response_type if self.response_type in ('xml', 'html') else 'xml'

        xml_ped = Util.get_xml_consultarCupoCUAD(numeroCuit)

        session = requests.Session()

        payload = {
            'messageRequest': xml_ped
        }

        self.logger.info('Params: ' + str(self.params))
        self.logger.info('Tx: ' + xml_ped)

        response = session.post(
            self.config.get('nbsf_brokerws', 'host') + self.config.get('nbsf_brokerws', 'resource'),
            data=payload
        )

        output = Util.format_replaceXMLEntities(response.content[122:-9])
        output = output.decode('utf-8') if self.response_type == 'xml' else Util.get_html_respuestaCUAD(self.env, output)
        self.logger.info('Rx: ' + re.sub('\s*\n\s*', '', output))

        Db.guardar_consulta(
            consulta=self.method,
            tx=xml_ped,
            rx=output,
            ip=self.client_ip
        )

        return output

    def cliConsBlqDesblq(self, operacion):
        self.response_type = self.params.get('formato', 'xml')[0]
        self.response_type = self.response_type if self.response_type in ('xml', 'html') else 'xml'

        if operacion == 8:  # Desbloqueo rechazado
            usuario = escape(str(self.params['usuario'][0]))
        else:
            usuario = None

        numeroCliente = escape(str(self.params['numeroCliente'][0]))
        xml_ped = Util.get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario)

        session = requests.Session()

        payload = {
            'Consulta': xml_ped
        }

        self.logger.info('Params: ' + str(self.params))
        self.logger.info('Tx: ' + xml_ped)

        response = session.post(
            self.config.get('nbsf_mensajeria', 'host') + self.config.get('nbsf_mensajeria', 'resource'),
            data=payload
        )

        output = Util.format_replaceXMLEntities(response.content)
        output = output if self.response_type == 'xml' else Util.get_html_respuestaDatosCliente(self.env, output)
        self.logger.info('Rx: ' + re.sub('\s*\n\s*', '', output))

        Db.guardar_consulta(
            consulta=self.method,
            tx=xml_ped,
            rx=output,
            ip=self.client_ip
        )

        return output

    def consultarCuotaMAForm(self):
        self.response_type = 'html'
        template_params = {'base_url': self.config.get('app', 'base_url')}

        return self.env.get_template('cuotaMA_form.html').render(template_params)

    def consultarCuotaMA(self):
        if not self.params:
            return self.consultarCuotaMAForm()

        self.response_type = 'html'
        uidPrestamo = escape(str(self.params['uidPrestamo'][0]))
        output = Util.get_html_respuestaCuotaMA(self.env, uidPrestamo)

        return output


application = Application()
