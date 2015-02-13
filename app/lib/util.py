# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
from ConfigParser import SafeConfigParser
from base64 import b64decode
from xml.dom import minidom
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
        xml_obj = minidom.parseString(xml)

        variables = {}
        texto_informe = ''

        for variable in xml_obj.getElementsByTagName('variable'):
            variables[variable.getElementsByTagName('nombre')[0].firstChild.data] = variable.getElementsByTagName('valor')[0].firstChild.data

        texto_informe = xml_obj.getElementsByTagName('informe')[0].getElementsByTagName('texto')[0].firstChild.data.encode('ascii', 'xmlcharrefreplace')
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
        periodo = xml_obj.findtext('.//{http://tempuri.org/CUADDS.xsd}Periodo', 'n/d')
        periodo = periodo[4:6] + ' / ' + periodo[0:4] if len(periodo) == 6 else periodo

        template_params = {
            'base_url': Util.config.get('app', 'base_url'),
            'variables': {
                'Nombre': xml_obj.findtext('.//{http://tempuri.org/CUADDS.xsd}NombreApellido', xml_obj.findtext('.//{http://tempuri.org/CUADDS.xsd}Descripcion')),
                u'Período': periodo,
                'Monto': xml_obj.findtext('.//{http://tempuri.org/CUADDS.xsd}Monto', 'n/d')
            }
        }

        return env.get_template('cuad_respuesta.html').render(template_params)
