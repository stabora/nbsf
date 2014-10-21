# -*- coding: utf-8 -*-

import os
import urlparse
import base64
import requests
import time
import logging
import re
import MySQLdb
from datetime import datetime
from cgi import escape
from ConfigParser import SafeConfigParser


class Application:

    def init(self, environ):
        self.baseDir = os.path.dirname(__file__)
        self.config = SafeConfigParser()
        self.config.read(os.path.join(self.baseDir, 'config.ini'))
        self.charset = 'utf-8'
        self.client_ip = self.get_client_ip(environ)

        self.db = MySQLdb.connect(
            host='localhost',
            user=self.config.get('mysql_nbsf', 'user'),
            passwd=self.config.get('mysql_nbsf', 'password'),
            db=self.config.get('mysql_nbsf', 'db')
        )

        self.cursor = self.db.cursor()

        logDir = os.path.join(self.baseDir, 'log', time.strftime('%Y'), time.strftime('%m'))

        if not os.path.exists(logDir):
            os.makedirs(logDir)
            os.chmod(logDir, 0777)

        logging.basicConfig(
            filename=os.path.join(logDir, 'nbsf_' + time.strftime('%Y%m%d') + '.log'),
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

        self.logger.info('Iniciado - IP: ' + self.client_ip)
        self.logger.info('Modo: ' + self.method)


        if uri_parsed.query:
            self.params = urlparse.parse_qs(uri_parsed.query)
        else:
            self.params = urlparse.parse_qs(environ.get('wsgi.input').read())


        if self.config.get('proxy', 'host'):
            self.proxies = {
                'http': (
                    'http://' +
                    self.config.get('proxy', 'user') + ':' +
                    base64.b64decode(self.config.get('proxy', 'pass')) + '@' +
                    self.config.get('proxy', 'host') + ':' +
                    self.config.get('proxy', 'port')
                ),
                'https': (
                    'http://' +
                    self.config.get('proxy', 'user') + ':' +
                    base64.b64decode(self.config.get('proxy', 'pass')) + '@' +
                    self.config.get('proxy', 'host') + ':' +
                    self.config.get('proxy', 'port')
                )
            }
        else:
            self.proxies = None

    def __call__(self, environ, start_response):
        self.init(environ)

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
                self.charset = 'iso-8859-1'

                nombre = escape(str(self.params['nombre'][0]))
                sexo = escape(str(self.params['sexo'][0]))
                numeroDocumento = escape(str(self.params['numeroDocumento'][0]))


                par_xml = self.get_xml_consultaVeraz(nombre, sexo, numeroDocumento)
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

                self.guardar_consulta(
                    consulta=self.method,
                    tx=par_xml,
                    rx=output
                )

            elif self.method == 'consultaPadron':
                response_type = 'xml'

                numeroDocumento = escape(str(self.params['numeroDocumento'][0]))
                xml_ped = self.get_xml_consultaPadron(numeroDocumento)

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

                self.guardar_consulta(
                    consulta=self.method,
                    tx=xml_ped,
                    rx=output
                )

            elif self.method == 'consultaCliente':
                response_type = 'xml'

                numeroCliente = escape(str(self.params['numeroCliente'][0]))
                xml_ped = self.get_xml_consultaCliente(numeroCliente)

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

                self.guardar_consulta(
                    consulta=self.method,
                    tx=xml_ped,
                    rx=output
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
            pass
            # output = output.replace(k, v)

        start_response(
            '200 OK',
            [('Content-Type', 'text/' + response_type + '; charset=' + self.charset)]
        )

        if self.charset == 'utf-8':
            return output.encode('utf-8')
        else:
            return output

    def get_client_ip(self, environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR']
        except KeyError:
            return environ['REMOTE_ADDR']

    def guardar_consulta(self, **kwargs):
        self.cursor.execute(
            'INSERT INTO consultas (consulta, tx, rx, ip) VALUES (%s, %s, %s, %s)',
            (
                kwargs['consulta'],
                kwargs['tx'],
                kwargs['rx'],
                self.client_ip
            )
        )

        self.db.commit()

    def get_xml_consultaVeraz(self, nombre, sexo, numeroDocumento):
        return (
            '<mensaje>'
            '<identificador>'
            '<userlogon>'
            '<matriz>' + self.config.get('veraz', 'matriz') + '</matriz>'
            '<usuario>' + self.config.get('veraz', 'usuario') + '</usuario>'
            '<password>' + self.config.get('veraz', 'password') + '</password>'
            '</userlogon>'
            '<medio>HTML</medio>'
            '<formatoInforme>T</formatoInforme>'
            '<reenvio/>'
            '<producto>RISC:Experto</producto>'
            '<lote>'
            '<sectorVeraz>03</sectorVeraz>'
            '<sucursalVeraz>0</sucursalVeraz>'
            '<cliente>TRA-999845721</cliente>'
            '<fechaHora>' +
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
            '</fechaHora>'
            '</lote>'
            '</identificador>'
            '<consulta>'
            '<integrantes>1</integrantes>'
            '<integrante valor="1">'
            '<nombre>' + nombre + '</nombre>'
            '<sexo>' + sexo + '</sexo>'
            '<documento>' + numeroDocumento + '</documento>'
            '</integrante>'
            '</consulta>'
            '</mensaje>'
        )

    def get_xml_consultaPadron(self, numeroDocumento):
        return (
            '<PedConsPad>'
            '<IDPedido>{}</IDPedido>'
            '<NroDoc>{}</NroDoc>'
            '</PedConsPad>'
        ).format(
            'NBSFPY-' + datetime.today().strftime('%Y%m%d%H%M'),
            numeroDocumento,
        )

    def get_xml_consultaCliente(self, numeroCliente):
        return (
            '<PedCliConsBlqDesblq>'
            '<IDPed>{}</IDPed>'
            '<Fecha>{}</Fecha>'
            '<Operacion>{}</Operacion>'
            '<NroCliente>{}</NroCliente>'
            '<Producto>{}</Producto>'
            '<User>{}</User>'
            '<Plataforma>WEB</Plataforma>'
            '</PedCliConsBlqDesblq>'
        ).format(
            'NBSFPY-' + datetime.today().strftime('%Y%m%d%H%M'),
            datetime.today().strftime('%Y%m%d'),
            1,  # Consulta
            numeroCliente,
            '0',
            'NBSFPY',
        )


application = Application()
