# -*- coding: utf-8 -*-

try:
    import cx_Oracle
except ImportError:
    pass

import re
import urllib2
from lxml import etree
from base64 import b64decode
from time import strptime
from app import app
from app.helpers.util import Util


class HTML:

    @staticmethod
    def get_html_respuestaVeraz(xml):
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        xml_obj = etree.fromstring(xml.encode('utf-8'), parser=parser)
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
        namespaces = {'ns': app.config['BROKERWS_XMLNS_CUAD']}
        xml_obj = etree.fromstring(xml)
        nombre = xml_obj.findtext('.//ns:NombreApellido', namespaces=namespaces)
        variables = {}

        if nombre:
            periodo = xml_obj.findtext('.//ns:Periodo', default='n/d', namespaces=namespaces)
            periodo = '{}/{}'.format(periodo[4:6], periodo[0:4]) if len(periodo) == 6 else periodo

            variables = {
                'Nombre': nombre,
                u'Período': periodo,
                'Monto': xml_obj.findtext('.//ns:Monto', default='n/d', namespaces=namespaces)
            }

        return variables

    @staticmethod
    def get_html_respuestaPrestamosPendientes(xml):
        variables = {}
        prestamos = []
        namespaces = {'ns': app.config['BROKERWS_XMLNS_PRESTAMOS']}

        xml_obj = etree.fromstring(xml)
        root = xml_obj.find('.//ns:PrestamosEnWFDS', namespaces=namespaces)

        if root is not None:
            for prestamo in root.getchildren():
                prestamos.append(prestamo.findtext('.//ns:IDWorkFlow', namespaces=namespaces))

        if prestamos:
            variables = {
                'totalPrestamos': len(prestamos),
                'tipoDocumento': root.findtext('.//ns:TipoDoc', namespaces=namespaces),
                'numeroDocumento': root.findtext('.//ns:NumeroDoc', namespaces=namespaces),
                'prestamos': prestamos
            }

        return variables

    @staticmethod
    def get_html_respuestaDatosCliente(xml):
        variables = {}
        namespaces = {'ns': app.config['MENSAJERIA_XMLNS']}

        xml_obj = etree.fromstring(xml)
        root = xml_obj.find('.//ns:ResCliConsBlqDesblq', namespaces=namespaces)

        if root is not None:
            codigo_respuesta = root.findtext('.//ns:CodEstadoPed', namespaces=namespaces)

            if codigo_respuesta == "100":
                for respuesta in root.getchildren():
                    if 'Respuesta' in respuesta.tag:
                        for nodo in respuesta.getchildren():
                            variables[Util.format_removeXMLNodeNamespace(nodo.tag)] = '' if nodo.text is None else nodo.text

        return variables

    @staticmethod
    def get_html_respuestaPadronElectoral(xml):
        variables = {}
        namespaces = {'ns': app.config['MENSAJERIA_XMLNS']}

        xml_obj = etree.fromstring(xml)
        root = xml_obj.find('.//ns:ResConsPad', namespaces=namespaces)

        if root:
            codigo_respuesta = root.findtext('.//ns:CodSubAs', namespaces=namespaces)

            if codigo_respuesta == "100":
                respuesta = root.find('.//ns:Respuesta', namespaces=namespaces)

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
                '''SELECT LEAST(CUOTA_A, CUOTA_B) CUOTA_MAXIMA, DATOS.*, '(IMC * ParamX) - Compromiso mensual' AS CUOTA_A_FORMULA, 'IMC * ParamY' AS CUOTA_B_FORMULA FROM (SELECT ((DATOS.IMC * DATOS.PARAM_X) - (DATOS.BUREAU_TTCC_PAGO_MINIMO + DATOS.BUREAU_PRESTAMOS_CUOTA)) AS CUOTA_A, (DATOS.IMC * DATOS.PARAM_Y) AS CUOTA_B, DATOS.* FROM (SELECT DATOS.*, (SELECT VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE   COD = 2016 AND SUBCOD = CASE WHEN DATOS.IMC < DATOS.PARAM_Y_IMC THEN 1 ELSE 2 END ) AS PARAM_Y FROM (SELECT SD.IMC, SD2.MA_TIPOVIVIENDA AS TIPO_VIVIENDA, EXTRACTVALUE(XMLTYPE.CREATEXML(CI.XMLRES), '//variables/variable/valor[../nombre/text() = "bureau_tarjetas_pago_minimo"]') AS BUREAU_TTCC_PAGO_MINIMO, EXTRACTVALUE(XMLTYPE.CREATEXML(CI.XMLRES), '//variables/variable/valor[../nombre/text() = "bureau_prestamos_cuota"]') AS BUREAU_PRESTAMOS_CUOTA, (SELECT VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE   COD = 2014 AND SUBCOD = SD2.MA_TIPOVIVIENDA ) AS PARAM_X, (SELECT VALOR FROM WF_PRESTAMOS.PARAMETROS WHERE   COD = 2015 AND SUBCOD = 0 ) AS PARAM_Y_IMC FROM WF_PRESTAMOS.SOLICITUDES SL INNER JOIN WF_PRESTAMOS.CON_X_INST CI ON CI."UID" = SL."UID"AND CI.CODCON = 31 INNER JOIN WF_PRESTAMOS.SOLICITUD_DETALLE SD ON SD."UID" = CI."UID"INNER JOIN WF_PRESTAMOS.SOLICITUD_DETALLE2 SD2 ON SD2."UID" = CI."UID"WHERE SL."UID" = :UID_PRESTAMOS ) DATOS ) DATOS ) DATOS''',
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
                cuotas['Cuota A [ {} ]'.format(datos[0]['CUOTA_A_FORMULA'])] = datos[0]['CUOTA_A']
                cuotas['Cuota B [ {} ]'.format(datos[0]['CUOTA_B_FORMULA'])] = datos[0]['CUOTA_B']

                parametros['IMC'] = datos[0]['IMC']
                parametros['Tipo vivienda'] = datos[0]['TIPO_VIVIENDA']
                parametros['Param X'] = datos[0]['PARAM_X']
                parametros['Param Y'] = datos[0]['PARAM_Y']
                parametros['Param Y IMC'] = datos[0]['PARAM_Y_IMC']
                parametros[u'Bureau pago mínimo TTCC'] = datos[0]['BUREAU_TTCC_PAGO_MINIMO']
                parametros[u'Bureau cuotas préstamos'] = datos[0]['BUREAU_PRESTAMOS_CUOTA']
                parametros[u'Compromiso mensual'] = float(datos[0]['BUREAU_PRESTAMOS_CUOTA']) + float(datos[0]['BUREAU_TTCC_PAGO_MINIMO'])

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
            return variables, 'Error al realizar la consulta - Motivo: {}'.format(e.message)

    @staticmethod
    def get_html_respuestaOperacionSoat(response):
        variables = {}

        for etiqueta, valor in response:
            variables[etiqueta] = valor

        return variables

    @staticmethod
    def get_html_respuestaLegajoDigital(response):
        documentos = []

        try:
            for documento in response.Documentos.DocumentoClienteOut:
                versiones = []
                documentoEtiqueta = documento.FormInterno

                for version in documento.Versiones.VersionDocumentoClienteOut:
                    archivos = []

                    if hasattr(version.Archivos, 'ArchivoOut'):
                        for archivo in version.Archivos.ArchivoOut:
                            archivoUrl = archivo.Permalink

                            try:
                                archivoTipo = urllib2.urlopen(archivoUrl).info().maintype
                            except:
                                archivoTipo = 'unknown'

                            archivos.append({
                                'id': archivo.IdArchivo,
                                'fecha': archivo.Fecha,
                                'nombre': archivo.Nombre,
                                'url': archivoUrl,
                                'urlMiniatura': archivo.PermalinkMiniatura,
                                'tipo': archivoTipo
                            })

                    if archivos:
                        versiones.append({
                            'numero': re.sub('[^0-9]', '', version.Version),
                            'fecha': version.FechaActu,
                            'archivos': sorted(archivos, key=lambda archivo: strptime(archivo['fecha'], '%d/%m/%Y') if archivo['fecha'] else None, reverse=True)
                        })

                if versiones:
                    documentos.append({
                        'id': documento.Id,
                        'descripcion': documento.Descripcion,
                        'etiqueta': documentoEtiqueta,
                        'versionable': documento.VersionaPorTramite,
                        'versiones': sorted(versiones, key=lambda version: '{}-{}'.format(strptime(version['fecha'], '%d/%m/%Y'), version['numero']) if version['fecha'] else None, reverse=True)
                    })
        except AttributeError:
            pass

        variables = {
            'documentos': documentos
        }

        return variables

    @staticmethod
    def get_html_respuestaPadronAFIP_A13(response):
        if response:
            xml = etree.fromstring(response)
            generales = {}
            contactos = {}
            actividades = {}
            impuestos = {}
            categorias = {}
            regimenes = {}
            titular = ''

            if not xml.findtext('.//faultstring'):
                if xml.findtext('.//persona/tipoPersona') == 'FISICA':
                    denominacion = '{}, {}'.format(xml.findtext('.//persona/apellido'), xml.findtext('.//persona/nombre'))
                else:
                    denominacion = xml.findtext('.//persona/razonSocial')

                titular = '{} ({})'.format(
                    denominacion,
                    '{}{}-{}{}{}{}{}{}{}{}-{}'.format(*xml.findtext('.//persona/idPersona'))
                )

                for valor in xml.find('.//persona'):
                    if len(valor) == 0:
                        generales[valor.tag] = valor.text

                c = 0

                for padre in xml.findall('.//persona/domicilio'):
                    titulo = 'N/D'
                    valores = {}

                    for nodo in padre.getchildren():
                        if nodo.tag == 'direccion':
                            c += 1
                            titulo = u'Domicilio #{} - {}'.format(c, nodo.text)
                        else:
                            valores[nodo.tag] = nodo.text

                    contactos[titulo] = valores

                c = 0

        variables = {
            'titular': titular,
            'generales': generales,
            'contactos': contactos,
            'actividades': actividades,
            'impuestos': impuestos,
            'regimenes': regimenes,
            'categorias': categorias,
        }

        return variables

    @staticmethod
    def get_html_respuestaPadronAFIP(response):
        if response:
            xml = etree.fromstring(response)
            generales = {}
            contactos = {}
            actividades = {}
            impuestos = {}
            categorias = {}
            regimenes = {}
            titular = ''

            if not xml.findtext('.//faultstring') and not xml.findtext('.//error'):
                if xml.findtext('.//datosGenerales/tipoPersona') == 'FISICA':
                    denominacion = '{}, {}'.format(xml.findtext('.//datosGenerales/apellido'), xml.findtext('.//datosGenerales/nombre'))
                else:
                    denominacion = xml.findtext('.//datosGenerales/razonSocial')

                titular = '{} ({})'.format(
                    denominacion,
                    '{}{}-{}{}{}{}{}{}{}{}-{}'.format(*xml.findtext('.//datosGenerales/idPersona'))
                )

                for valor in xml.find('.//datosGenerales'):
                    if len(valor) == 0:
                        generales[valor.tag] = valor.text

                c = 0

                for padre in xml.findall('.//domicilioFiscal'):
                    titulo = 'N/D'
                    valores = {}

                    for nodo in padre.getchildren():
                        if nodo.tag == 'direccion':
                            c += 1
                            titulo = u'Domicilio #{} - {}'.format(c, nodo.text)
                        else:
                            valores[nodo.tag] = nodo.text

                    contactos[titulo] = valores

                c = 0

                for padre in xml.findall('.//actividad'):
                    titulo = 'N/D'
                    valores = {}

                    for nodo in padre.getchildren():
                        if 'descripcion' in nodo.tag:
                            titulo = nodo.text
                        else:
                            valores[nodo.tag] = nodo.text

                            if 'orden' in nodo.tag:
                                titulo = u'{} - {}'.format(nodo.text, titulo)

                    actividades[titulo] = valores

                for padre in xml.findall('.//actividadMonotributista'):
                    titulo = 'N/D'
                    valores = {}

                    for nodo in padre.getchildren():
                        if 'descripcionActividad' in nodo.tag:
                            titulo = nodo.text
                        else:
                            valores[nodo.tag] = nodo.text

                    actividades[titulo] = valores

                for padre in xml.findall('.//impuesto'):
                    titulo = 'N/D'
                    valores = {}

                    for nodo in padre.getchildren():
                        if 'descripcion' in nodo.tag:
                            titulo = nodo.text
                        else:
                            valores[nodo.tag] = nodo.text

                    impuestos[titulo] = valores

                for padre in xml.findall('.//regimen'):
                    titulo = 'N/D'
                    valores = {}

                    for nodo in padre.getchildren():
                        if 'descripcion' in nodo.tag:
                            titulo = nodo.text
                        else:
                            valores[nodo.tag] = nodo.text

                    regimenes[titulo] = valores

                for padre in xml.findall('.//categoriaMonotributo'):
                    titulo = 'N/D'
                    valores = {}

                    for nodo in padre.getchildren():
                        if 'descripcionCategoria' in nodo.tag:
                            titulo = nodo.text
                        else:
                            valores[nodo.tag] = nodo.text

                    categorias[titulo] = valores

        variables = {
            'titular': titular,
            'generales': generales,
            'contactos': contactos,
            'actividades': actividades,
            'impuestos': impuestos,
            'regimenes': regimenes,
            'categorias': categorias,
        }

        return variables
