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

if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

from lib.nbsf import NBSF
from lib.db import Db


class Application:

    baseDir = os.path.dirname(__file__)
    config = SafeConfigParser()
    config.read(os.path.join(baseDir, 'config.ini'))

    def __call__(self, environ, start_response):
        self.init(environ)
        charset = 'utf-8'

        self.logger.info('Iniciado - IP: ' + self.client_ip)
        self.logger.info('Modo: ' + self.method)

        try:
            output = ''

            if self.method == 'consultaVerazForm':
                response_type = 'html'

                output += (
                    open(self.baseDir + '/views/veraz/form.html').read() %
                    {
                        'host': self.hostname,
                        'baseUri': self.baseUri
                    }
                )

            elif self.method == 'consultaVeraz':
                if not self.params:
                    start_response(
                        '301 Redirect',
                        [('Location', 'http://' + self.hostname + '/' + self.baseUri + '/consultaVerazForm')]
                    )

                    return output

                response_type = 'xml'
                charset = 'iso-8859-1'

                nombre = escape(str(self.params['nombre'][0]))
                sexo = escape(str(self.params['sexo'][0]))
                numeroDocumento = escape(str(self.params['numeroDocumento'][0]))

                par_xml = NBSF.get_xml_consultaVeraz(nombre, sexo, numeroDocumento)

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

                output += response.content
                self.logger.info('Rx: ' + re.sub('\s*\n\s*', '', output))

                Db.guardar_consulta(
                    consulta=self.method,
                    tx=par_xml,
                    rx=output,
                    ip=self.client_ip
                )

            elif self.method == 'consultaPadron':
                response_type = 'xml'

                numeroDocumento = escape(str(self.params['numeroDocumento'][0]))
                xml_ped = NBSF.get_xml_consultaPadron(numeroDocumento)

                session = requests.Session()

                payload = {
                    'Consulta': xml_ped
                }

                self.logger.info('numeroDocumento: ' + numeroDocumento)
                self.logger.info('Tx: ' + xml_ped)

                response = session.post(
                    self.config.get('nbsf_mensajeria', 'host') + self.config.get('nbsf_mensajeria', 'resource'),
                    data=payload
                )

                output += response.content
                self.logger.info('Rx: ' + re.sub('\s*\n\s*', '', output))

                Db.guardar_consulta(
                    consulta=self.method,
                    tx=xml_ped,
                    rx=output,
                    ip=self.client_ip
                )

            elif self.method == 'consultaCliente':
                response_type = 'xml'

                numeroCliente = escape(str(self.params['numeroCliente'][0]))
                xml_ped = NBSF.get_xml_consultaCliente(numeroCliente)

                session = requests.Session()

                payload = {
                    'Consulta': xml_ped
                }

                self.logger.info('numeroCliente: ' + numeroCliente)
                self.logger.info('Tx: ' + xml_ped)

                response = session.post(
                    self.config.get('nbsf_mensajeria', 'host') + self.config.get('nbsf_mensajeria', 'resource'),
                    data=payload
                )

                output += response.content
                self.logger.info('Rx: ' + re.sub('\s*\n\s*', '', output))

                Db.guardar_consulta(
                    consulta=self.method,
                    tx=xml_ped,
                    rx=output,
                    ip=self.client_ip
                )

            else:
                response_type = 'html'
                output += open(self.baseDir + '/views/welcome.html').read()

        except (KeyError, IndexError) as e:
            response_type = 'xml'
            self.logger.error(u'Error: ' + str(e.message))
            output += '<error><![CDATA[Error inesperado: {}]]></error>'.format(e.message)

        except Exception as e:
            response_type = 'xml'
            self.logger.error(u'Error: ' + str(e.message))
            output += '<error><![CDATA[Error inesperado: {}]]></error>'.format(e.message)

        self.logger.info('Finalizado\n')
        logging.shutdown()

        for k, v in [('&lt;', '<'), ('&gt;', '>')]:
            output = output.replace(k, v)

        start_response(
            '200 OK',
            [('Content-Type', 'text/' + response_type + '; charset=' + charset)]
        )

        if charset == 'utf-8':
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

        self.proxies = NBSF.get_proxies()

    def get_client_ip(self, environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR']
        except KeyError:
            return environ['REMOTE_ADDR']


application = Application()
