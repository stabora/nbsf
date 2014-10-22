# -*- coding: utf-8 -*-

import os
from datetime import datetime
from ConfigParser import SafeConfigParser
from base64 import b64decode


class NBSF:

    baseDir = os.path.dirname(os.path.dirname(__file__))
    config = SafeConfigParser()
    config.read(os.path.join(baseDir, 'config.ini'))


    @staticmethod
    def get_proxies():
        proxies = {}

        if NBSF.config.get('proxy', 'host'):
            for protocol in ('http', 'https'):
                proxies.update({
                    protocol: (
                        'http://' +
                        NBSF.config.get('proxy', 'user') + ':' +
                        b64decode(NBSF.config.get('proxy', 'pass')) + '@' +
                        NBSF.config.get('proxy', 'host') + ':' +
                        NBSF.config.get('proxy', 'port')
                    )
                })

        return proxies

    @staticmethod
    def get_xml_consultaPadron(numeroDocumento):
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
    def get_xml_consultaCliente(numeroCliente):
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

    @staticmethod
    def get_xml_consultaVeraz(nombre, sexo, numeroDocumento):
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
            NBSF.config.get('veraz', 'matriz'),
            NBSF.config.get('veraz', 'usuario'),
            NBSF.config.get('veraz', 'password'),
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            nombre,
            sexo,
            numeroDocumento,
        )