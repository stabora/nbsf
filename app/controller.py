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
from xml.dom import minidom
from jinja2 import Environment, FileSystemLoader

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
                template = self.env.get_template('form_veraz.html')

                output = template.render()

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

            elif self.method == 'testXML':
                template = self.env.get_template('respuesta_veraz.html')
                xml_obj = minidom.parseString('<mensaje><estado><codigoError>0</codigoError><mensajeError></mensajeError></estado><identificador><fechaRecepcion>2014-10-22 15:10:39</fechaRecepcion><lote>201410226707476</lote><producto>RISC:Experto</producto><cliente>TRA-999845721</cliente></identificador><respuesta><grupo><variables></variables></grupo><integrantes>1</integrantes><integrante valor="1"><nombre>TABORA,SEBASTIAN OMAR                                                   </nombre><documento>26160465</documento><sexo>M</sexo><variables><variable><nombre clase="A"><![CDATA[Documento]]></nombre><valor tipo="N"><![CDATA[26160465]]></valor></variable><variable><nombre clase="A"><![CDATA[Sexo]]></nombre><valor tipo="C"><![CDATA[M]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_prestamos_cuota]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_prestamos_cuota_res]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_prestamos_saldo_total]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_tarjetas_limite_compra]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_tarjetas_pago_minimo]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_tarjetas_saldo_total]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[bureau_ultimo_estado_4M]]></nombre><valor tipo="C"><![CDATA[-]]></valor></variable><variable><nombre clase="A"><![CDATA[cantidad_consultas_financieras]]></nombre><valor tipo="N"><![CDATA[1]]></valor></variable><variable><nombre clase="O"><![CDATA[categoria]]></nombre><valor tipo="C"><![CDATA[rechazar]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_1]]></nombre><valor tipo="C"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_2]]></nombre><valor tipo="C"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_3]]></nombre><valor tipo="C"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_4]]></nombre><valor tipo="C"><![CDATA[1]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_5]]></nombre><valor tipo="C"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[cuota]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[cuota_maxima_sugerida]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[explicacion]]></nombre><valor tipo="C"><![CDATA[Ingreso promedio menor a 5000]]></valor></variable><variable><nombre clase="O"><![CDATA[maximo_limite]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[maximo_limite_ACC]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[observaciones_concursos_quiebras]]></nombre><valor tipo="C"><![CDATA[No]]></valor></variable><variable><nombre clase="A"><![CDATA[observaciones_juicios]]></nombre><valor tipo="C"><![CDATA[No]]></valor></variable><variable><nombre clase="A"><![CDATA[observaciones_morosidad]]></nombre><valor tipo="C"><![CDATA[No]]></valor></variable><variable><nombre clase="O"><![CDATA[relacion_compromiso_ingresos]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[relacion_cuota_ingresos]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[score_poblacion]]></nombre><valor tipo="C"><![CDATA[th]]></valor></variable><variable><nombre clase="O"><![CDATA[score_veraz]]></nombre><valor tipo="N"><![CDATA[665]]></valor></variable><variable><nombre clase="A"><![CDATA[total_sugerido_limite_ACC]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[total_sugerido_limite_tarjeta]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[validacion]]></nombre><valor tipo="C"><![CDATA[Validado]]></valor></variable><variable><nombre clase="A"><![CDATA[version_DNI]]></nombre><valor tipo="C"><![CDATA[Original]]></valor></variable></variables></integrante><informe><html/><texto><![CDATA[001T00000100C010000                                    VERAZ RISC001T00000200C010000             NUEVO BANCO DE SANTA FE              CONSULTA001T00000300C010000             LOTE:6707476-VN0330000003 EMITIDO EL 22/10/2014 (INFORME 01/01)001T00000400E040000Este informe que solicitara en su calidad de cliente, es confidencial y001T00000500E040000solo debera usarse para la evaluacion y celebracion de negocios.001T00000600E040000Prohibida su reproduccion, divulgacion y entrega a terceros (Deber de001T00000700E040000confidencialidad y uso permitido - Ley 25.326). No contiene juicios de001T00000800E040000valor sobre las personas ni sobre su solvencia. Las decisiones a las que001T00000900E040000arribe el usuario son de su exclusiva responsabilidad.001T00001010T020000DATOS SEGUN SU CONSULTA EFECTUADA EL: 22/10/2014001T00001110L010000      TABORA,SEBASTIAN OMAR  CLIENTE: TRA-999845721001T00001210L010000      DNI= 26.160.465001T00001315T020000DATOS SEGUN BASE DE VALIDACION VERAZ:001T00001415H010000      DNI 26.160.465 VALIDADO (ORIGINAL)001T00001515L010000      TABORA,SEBASTIAN OMAR                         EDAD=36  FECHA=14/11/1977001T00001615L010000      GOROSTIAGA 3810   (2000) (S2001LED) ROSARIO SANTA FE001T00001788L010000      CDI  20-26160465-6001T00001820T010000                       DATOS SEGUN BASE DE INFORMACION:001T00001930T020000                        OBSERVACIONES (ULTIMOS 5 AÑOS)001T00002030Z010000NO REGISTRA001T00002140T050000             VERAZ CREDIT BUREAU (FUENTE PROPIA - ULTIMOS 5 AÑOS)001T00002240S010000NO REGISTRA001T00002330T08CH00        CHEQUES RECHAZADOS AL: 21/10/2014  (FUENTE BCRA - ULTIMOS 2 AÑOS)001T00002430Z07CH00NO REGISTRA001T00002537T00000        DEUDORES DEL SISTEMA FINANCIERO (FUENTE BCRA - ULTIMOS 2 AÑOS)001T00002637S010000NO REGISTRA001T00002750T020000                          CONSULTAS (ULTIMOS 5 AÑOS)001T00002850Z010000FECHA   EMPRESA/ENTIDAD001T00002950S010000SECTOR FINANCIERO001T00003050L01010010/2014 NUEVO BANCO DE SANTA FE001T00003199L030000            =========================================================001T00003299H020000            FIN DEL INFORME 01/01 REFERENCIA:1012780824#ZWQKZZZQYZOFB001T00003399L010000]]></texto></informe></respuesta></mensaje>')

                response_type = 'html'

                variables = {}

                for variable in xml_obj.getElementsByTagName('variable'):
                    variables[variable.getElementsByTagName('nombre')[0].firstChild.data] = variable.getElementsByTagName('valor')[0].firstChild.data

                texto_informe = xml_obj.getElementsByTagName('informe')[0].getElementsByTagName('texto')[0].firstChild.data.encode('ascii', 'xmlcharrefreplace')
                texto_informe = re.sub(r'[0-9]{3}[A-Z][0-9]{8}[A-Z\*][0-9]{2}[0-9A-Z]{2}[0-9]{1,2}', '<br>', texto_informe)

                output = template.render(variables=variables, texto_informe=texto_informe)

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

        self.env = Environment(
            autoescape=True, 
            loader=FileSystemLoader(os.path.join(self.baseDir, 'templates'))
        )

    def get_client_ip(self, environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR']
        except KeyError:
            return environ['REMOTE_ADDR']


application = Application()
