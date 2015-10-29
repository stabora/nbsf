# -*- coding: utf-8 -*-

try:
    import cx_Oracle
except ImportError:
    pass

import re
from lxml import etree
from base64 import b64decode
from app.helpers.util import Util
from app import app


class HTML:

    @staticmethod
    def get_html_respuestaVeraz(xml):
        xml_obj = etree.fromstring(xml)
        codigo_error = xml_obj.findtext('.//codigoError')
        variables = {}
        texto_informe = ''
        texto_error = ''

        if codigo_error == "0":
            for variable in xml_obj.findall('.//variable'):
                variables[variable.findtext('nombre')] = variable.findtext('valor')

            texto_informe = xml_obj.findtext('.//informe/texto')
            texto_informe = re.sub(r'\n', '', texto_informe)
            texto_informe = re.sub(r'[0-9]{3}[A-Z][0-9]{8}[A-Z\*][0-9]{2}[0-9A-Z]{2}[0-9]{1,2}', '<br>', texto_informe)
        else:
            texto_error = xml_obj.findtext('.//mensajeError')

        return {
            'variables': variables,
            'texto_informe': texto_informe,
            'texto_error': texto_error
        }

    @staticmethod
    def get_html_respuestaCupoCUAD(xml):
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

        return variables

    @staticmethod
    def get_html_respuestaPrestamosPendientes(xml):
        variables = {}
        prestamos = []

        xml_obj = etree.fromstring(xml)
        root = xml_obj.find('.//{http://tempuri.org/PrestamosEnWFDS.xsd}PrestamosEnWFDS')

        if root is not None:
            for prestamo in root.getchildren():
                prestamos.append(prestamo.findtext('.//{http://tempuri.org/PrestamosEnWFDS.xsd}IDWorkFlow'))

        if prestamos:
            variables = {
                'totalPrestamos': len(prestamos),
                'tipoDocumento': root.findtext('.//{http://tempuri.org/PrestamosEnWFDS.xsd}TipoDoc'),
                'numeroDocumento': root.findtext('.//{http://tempuri.org/PrestamosEnWFDS.xsd}NumeroDoc'),
                'prestamos': prestamos
            }

        return variables

    @staticmethod
    def get_html_respuestaDatosCliente(xml):
        variables = {}

        xml_obj = etree.fromstring(xml)
        root = xml_obj.find('.//{http://tempuri.org/}ResCliConsBlqDesblq')

        if root is not None:
            codigo_respuesta = root.findtext('.//{http://tempuri.org/}CodEstadoPed')

            if codigo_respuesta == "100":
                for respuesta in root.getchildren():
                    if 'Respuesta' in respuesta.tag:
                        for nodo in respuesta.getchildren():
                            variables[Util.format_removeXMLNodeNamespace(nodo.tag)] = '' if nodo.text is None else nodo.text

        return variables

    @staticmethod
    def get_html_respuestaPadronElectoral(xml):
        variables = {}

        xml_obj = etree.fromstring(xml)
        root = xml_obj.find('.//{http://tempuri.org/}ResConsPad')

        if root:
            codigo_respuesta = root.findtext('.//{http://tempuri.org/}CodSubAs')

            if codigo_respuesta == "100":
                respuesta = root.find('.//{http://tempuri.org/}Respuesta')

                for nodo in respuesta.getchildren():
                    variables[Util.format_removeXMLNodeNamespace(nodo.tag)] = '' if nodo.text is None else nodo.text

        return variables

    @staticmethod
    def get_html_respuestaCuotaMA(uidPrestamo):
        variables = {}

        try:
            db = cx_Oracle.connect(
                '{}/{}@{}/{}'.format(
                    app.config['ORACLE_NBSF_WF6_USER'],
                    b64decode(app.config['ORACLE_NBSF_WF6_PASSWORD']),
                    app.config['ORACLE_NBSF_WF6_HOST'],
                    app.config['ORACLE_NBSF_WF6_SID']
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

            variables = {
                'uidPrestamo': uidPrestamo,
                'cuotas': cuotas,
                'parametros': parametros,
                'valoresParamX': valoresParamX,
                'valoresParamY': valoresParamY
            }

            cursor.close()
            db.close()

            return variables, None
        except Exception, e:
            return variables, 'Error al realizar la consulta - Motivo: ' + str(e.message)

    @staticmethod
    def get_html_respuestaOperacionSoat(xml):
        variables = {}
        xml_obj = etree.fromstring(xml)
        nodos = xml_obj.xpath("//Envelope/Body/*/*/*")

        if nodos is not None:
            for nodo in nodos:
                variables[Util.format_removeXMLNodeNamespace(nodo.tag)] = nodo.text

        return variables
