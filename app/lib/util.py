# -*- coding: utf-8 -*-

import os
import re
import cx_Oracle
from datetime import datetime
from ConfigParser import SafeConfigParser
from base64 import b64decode
from random import randint
from lxml import etree


class Util:

    baseDir = os.path.dirname(os.path.dirname(__file__))
    config = SafeConfigParser()
    config.read(os.path.join(baseDir, 'config.ini'))

    @staticmethod
    def format_replaceXMLEntities(xml):
        for k, v in [('&lt;', '<'), ('&gt;', '>')]:
            xml = xml.replace(k, v)

        return xml

    @staticmethod
    def cursor_to_dict(cursor):
        columns = [i[0] for i in cursor.description]
        return [dict(zip(columns, row)) for row in cursor]

    @staticmethod
    def get_proxies():
        proxies = {}

        if Util.config.get('proxy', 'host'):
            for protocol in ('http', 'https'):
                proxies.update({
                    protocol: (
                        'http://' +
                        Util.config.get('proxy', 'user') + ':' +
                        b64decode(Util.config.get('proxy', 'pass')) + '@' +
                        Util.config.get('proxy', 'host') + ':' +
                        Util.config.get('proxy', 'port')
                    )
                })

        return proxies

    @staticmethod
    def get_xml_consultarPadron(numeroDocumento):
        return (
            '<PedConsPad>'
            '<IDPedido>{}</IDPedido>'
            '<NroDoc>{}</NroDoc>'
            '</PedConsPad>'
        ).format(
            'NBSFPY-' + datetime.today().strftime('%Y%m%d%H%M'),
            numeroDocumento,
        )

    @staticmethod
    def get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario=None):
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
            operacion,
            numeroCliente,
            '0',
            'NBSFPY' if usuario is None else usuario,
        )

    @staticmethod
    def get_xml_consultarCupoCUAD(cuit):
        return (
            '<Request>'
            '<Header>'
            '<ActionCode>NBSF.PrestamosEnComercios.CUAD.ConsultarCupoQuery</ActionCode>'
            '<TraceGuid>00000000-0000-0000-0000-000{traceGuid:09d}</TraceGuid>'
            '<IsBodyEncrypted>false</IsBodyEncrypted>'
            '<EncryptRequest>false</EncryptRequest>'
            '<EncryptResponse>false</EncryptResponse>'
            '</Header>'
            '<Body>'
            '<DSData>'
            '<xs:schema attributeFormDefault="qualified" elementFormDefault="qualified" id="CUADDS" targetNamespace="http://tempuri.org/CUADDS.xsd" xmlns="http://tempuri.org/CUADDS.xsd" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:mstns="http://tempuri.org/CUADDS.xsd" xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:element name="CUADDS">'
            '<xs:complexType>'
            '<xs:choice maxOccurs="unbounded" minOccurs="0">'
            '<xs:element name="ConsultaCupo">'
            '<xs:complexType>'
            '<xs:sequence>'
            '<xs:element name="ClaveEmpleado" type="xs:string"/>'
            '<xs:element minOccurs="0" name="CUIL" type="xs:long"/>'
            '<xs:element name="IdEmpleador" type="xs:int"/>'
            '</xs:sequence>'
            '</xs:complexType>'
            '</xs:element>'
            '</xs:choice>'
            '</xs:complexType>'
            '</xs:element>'
            '</xs:schema>'
            '<diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
            '<CUADDS xmlns="http://tempuri.org/CUADDS.xsd">'
            '<ConsultaCupo>'
            '<ClaveEmpleado>{cuit}</ClaveEmpleado>'
            '<CUIL>{cuit}</CUIL>'
            '<IdEmpleador>{idEmpleador}</IdEmpleador>'
            '</ConsultaCupo>'
            '</CUADDS>'
            '</diffgr:diffgram>'
            '</DSData>'
            '</Body>'
            '</Request>'
        ).format(
            traceGuid=randint(1, 999999999),
            cuit=cuit,
            idEmpleador=10
        )

    @staticmethod
    def get_xml_consultarVeraz(nombre, sexo, numeroDocumento):
        return (
            '<mensaje>'
            '<identificador>'
            '<userlogon>'
            '<matriz>{}</matriz>'
            '<usuario>{}</usuario>'
            '<password>{}</password>'
            '</userlogon>'
            '<medio>HTML</medio>'
            '<formatoInforme>T</formatoInforme>'
            '<reenvio/>'
            '<producto>RISC:Experto</producto>'
            '<lote>'
            '<sectorVeraz>03</sectorVeraz>'
            '<sucursalVeraz>0</sucursalVeraz>'
            '<cliente>TRA-999845721</cliente>'
            '<fechaHora>{}</fechaHora>'
            '</lote>'
            '</identificador>'
            '<consulta>'
            '<integrantes>1</integrantes>'
            '<integrante valor="1">'
            '<nombre>{}</nombre>'
            '<sexo>{}</sexo>'
            '<documento>{}</documento>'
            '</integrante>'
            '</consulta>'
            '</mensaje>'
        ).format(
            Util.config.get('veraz', 'matriz'),
            Util.config.get('veraz', 'usuario'),
            Util.config.get('veraz', 'password'),
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            nombre,
            sexo,
            numeroDocumento,
        )

    @staticmethod
    def get_html_respuestaVeraz(env, xml):
        xml_obj = etree.fromstring(xml)
        codigo_error = xml_obj.findtext('.//codigoError')
        variables = {}
        texto_informe = ''

        if codigo_error == "0":
            for variable in xml_obj.findall('.//variable'):
                variables[variable.findtext('nombre')] = variable.findtext('valor')

            texto_informe = xml_obj.findtext('.//informe/texto').encode('ascii', 'xmlcharrefreplace')
            texto_informe = re.sub(r'\n', '', texto_informe)
            texto_informe = re.sub(r'[0-9]{3}[A-Z][0-9]{8}[A-Z\*][0-9]{2}[0-9A-Z]{2}[0-9]{1,2}', '<br>', texto_informe)

        template_params = {
            'base_url': Util.config.get('app', 'base_url'),
            'variables': variables,
            'texto_informe': texto_informe
        }

        return env.get_template('veraz_respuesta.html').render(template_params)

    @staticmethod
    def get_html_respuestaCUAD(env, xml):
        xml_obj = etree.fromstring(xml)
        nombre = xml_obj.findtext('.//{http://tempuri.org/CUADDS.xsd}NombreApellido')
        variables = {}

        if nombre:
            periodo = xml_obj.findtext('.//{http://tempuri.org/CUADDS.xsd}Periodo', 'n/d')
            periodo = periodo[4:6] + ' / ' + periodo[0:4] if len(periodo) == 6 else periodo

            variables = {
                'Nombre': nombre,
                u'Período': periodo,
                'Monto': xml_obj.findtext('.//{http://tempuri.org/CUADDS.xsd}Monto', 'n/d')
            }

        template_params = {
            'base_url': Util.config.get('app', 'base_url'),
            'variables': variables
        }

        return env.get_template('cuad_respuesta.html').render(template_params)

    @staticmethod
    def get_html_respuestaDatosCliente(env, xml):
        xml_obj = etree.fromstring(xml)
        root = xml_obj.find('.//{http://tempuri.org/}ResCliConsBlqDesblq')
        codigo_respuesta = root.findtext('.//{http://tempuri.org/}CodEstadoPed')
        variables = {}

        if codigo_respuesta == "100":
            for respuesta in root.getchildren():
                if 'Respuesta' in respuesta.tag:
                    for nodo in respuesta.getchildren():
                        variables[re.sub(r'\{[a-z.:/]+\}', '', nodo.tag)] = '' if nodo.text is None else nodo.text

        template_params = {
            'base_url': Util.config.get('app', 'base_url'),
            'variables': variables
        }

        return env.get_template('consultarCliente_respuesta.html').render(template_params)

    @staticmethod
    def get_html_respuestaCuotaMA(env, uidPrestamo):
        db = cx_Oracle.connect(
            '{}/{}@{}/{}'.format(
                Util.config.get('oracle_nbsf_wf6', 'user'),
                Util.config.get('oracle_nbsf_wf6', 'password'),
                Util.config.get('oracle_nbsf_wf6', 'host'),
                Util.config.get('oracle_nbsf_wf6', 'sid')
            )
        )

        cursor = db.cursor()

        cursor.execute(
            '''SELECT LEAST(CUOTA_A, CUOTA_B) CUOTA_MAXIMA, DATOS.*, '(IMC * ParamX) - Compromiso mensual' AS CUOTA_A_FORMULA, 'IMC * ParamY' AS CUOTA_B_FORMULA FROM (SELECT ((DATOS.IMC * DATOS.PARAM_X) - (DATOS.BUREAU_TTCC_PAGO_MINIMO + DATOS.BUREAU_PRESTAMOS_CUOTA_RES)) AS CUOTA_A, (DATOS.IMC * DATOS.PARAM_Y) AS CUOTA_B, DATOS.* FROM (SELECT DATOS.*, (SELECT VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE   COD = 2016 AND SUBCOD = CASE WHEN DATOS.IMC < DATOS.PARAM_Y_IMC THEN 1 ELSE 2 END ) AS PARAM_Y FROM (SELECT SD.IMC, SD2.MA_TIPOVIVIENDA AS TIPO_VIVIENDA, EXTRACTVALUE(XMLTYPE.CREATEXML(CI.XMLRES), '//variables/variable/valor[../nombre/text() = "bureau_tarjetas_pago_minimo"]') AS BUREAU_TTCC_PAGO_MINIMO, EXTRACTVALUE(XMLTYPE.CREATEXML(CI.XMLRES), '//variables/variable/valor[../nombre/text() = "bureau_prestamos_cuota_res"]') AS BUREAU_PRESTAMOS_CUOTA_RES, (SELECT VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE   COD = 2014 AND SUBCOD = SD2.MA_TIPOVIVIENDA ) AS PARAM_X, (SELECT VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE   COD = 2015 AND SUBCOD = 0 ) AS PARAM_Y_IMC FROM WF_PRESTAMOS.SOLICITUDES SL INNER JOIN WF_PRESTAMOS.CON_X_INST CI ON CI."UID" = SL."UID"AND CI.CODCON = 31 INNER JOIN WF_PRESTAMOS.SOLICITUD_DETALLE SD ON SD."UID" = CI."UID"INNER JOIN WF_PRESTAMOS.SOLICITUD_DETALLE2 SD2 ON SD2."UID" = CI."UID"WHERE SL."UID" = :UID_PRESTAMOS ) DATOS ) DATOS ) DATOS''',
            [uidPrestamo]
        )

        datos = Util.cursor_to_dict(cursor)

        cursor.execute(
            'SELECT SUBCOD, DESCRIPCION, VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE COD = :COD AND SUBCOD > 0 ORDER BY SUBCOD',
            [2014]
        )

        valoresParamX = Util.cursor_to_dict(cursor)

        cursor.execute(
            'SELECT SUBCOD, DESCRIPCION, VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE COD = :COD AND SUBCOD > 0 ORDER BY SUBCOD',
            [2016]
        )

        valoresParamY = Util.cursor_to_dict(cursor)

        cuotas = {}
        parametros = {}

        if datos:
            cuotas[u'Cuota máxima'] = datos[0]['CUOTA_MAXIMA'] if float(datos[0]['CUOTA_MAXIMA']) > 0 else 0
            cuotas['Cuota A [ ' + datos[0]['CUOTA_A_FORMULA'] + ' ]'] = datos[0]['CUOTA_A']
            cuotas['Cuota B [ ' + datos[0]['CUOTA_B_FORMULA'] + ' ]'] = datos[0]['CUOTA_B']

            parametros['IMC'] = datos[0]['IMC']
            parametros['Tipo vivienda'] = datos[0]['TIPO_VIVIENDA']
            parametros['Param X'] = datos[0]['PARAM_X']
            parametros['Param Y'] = datos[0]['PARAM_Y']
            parametros['Param Y IMC'] = datos[0]['PARAM_Y_IMC']
            parametros[u'Bureau pago mínimo TTCC'] = datos[0]['BUREAU_TTCC_PAGO_MINIMO']
            parametros[u'Bureau cuotas préstamos'] = datos[0]['BUREAU_PRESTAMOS_CUOTA_RES']
            parametros[u'Compromiso mensual'] = float(datos[0]['BUREAU_PRESTAMOS_CUOTA_RES']) + float(datos[0]['BUREAU_TTCC_PAGO_MINIMO'])

        template_params = {
            'base_url': Util.config.get('app', 'base_url'),
            'cuotas': cuotas,
            'parametros': parametros,
            'valoresParamX': valoresParamX,
            'valoresParamY': valoresParamY
        }

        cursor.close()
        db.close()

        return env.get_template('cuotaMA_respuesta.html').render(template_params)
