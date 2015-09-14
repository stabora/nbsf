# -*- coding: utf-8 -*-

from xml import XML
from app import app
from app.helpers.util import Util


class Mensajeria:

    @staticmethod
    def cliConsBlqDesblq(operacion, numeroCliente, usuario='NBSFPY'):
        xml_ped = XML.get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario)

        response, msg = Util.get_http_request(
            app.config['NBSF_MENSAJERIA_HOST'] + app.config['NBSF_MENSAJERIA_RESOURCE'],
            {'Consulta': xml_ped},
            trust_env=False
        )

        return response, xml_ped, msg
