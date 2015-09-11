# -*- coding: utf-8 -*-

from flask import request
from xml import XML
from app import app
from app.helpers.util import Util
from app.helpers.db import Db


class Mensajeria:

    @staticmethod
    def cliConsBlqDesblq(operacion, numeroCliente, usuario='NBSFPY'):
        xml_ped = XML.get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario)

        response = Util.format_replaceXMLEntities(Util.get_http_request(
            app.config['NBSF_MENSAJERIA_HOST'] + app.config['NBSF_MENSAJERIA_RESOURCE'],
            {'Consulta': xml_ped},
            trust_env=False
        ).content)

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=xml_ped,
            rx=response,
            ip=request.remote_addr
        )

        return response
