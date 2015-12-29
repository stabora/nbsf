# -*- coding: utf-8 -*-

from xml import XML
from app import app
from app.helpers.util import Util


class Mensajeria:

    @staticmethod
    def cliConsBlqDesblq(operacion, numeroCliente, usuario='NBSFPY', entorno='DESARROLLO'):
        xml_ped = XML.get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario)

        response, msg = Util.get_http_request(
            '{}{}'.format(
              app.config['MENSAJERIA_HOST_{}'.format(entorno)],
              app.config['MENSAJERIA_RESOURCE']
            ),
            {'Consulta': xml_ped},
            trust_env=False
        )

        return response, xml_ped, msg
