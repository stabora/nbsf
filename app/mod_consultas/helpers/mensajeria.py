import requests
from flask import request
from xml import XML
from app import app
from app.helpers.util import Util
from app.helpers.db import Db


class Mensajeria:

    @staticmethod
    def cliConsBlqDesblq(operacion, numeroCliente, usuario='NBSFPY'):
        xml_ped = XML.get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario)

        session = requests.Session()

        payload = {
            'Consulta': xml_ped
        }

        response = session.post(
            app.config['NBSF_MENSAJERIA_HOST'] + app.config['NBSF_MENSAJERIA_RESOURCE'],
            data=payload
        )

        response = Util.format_replaceXMLEntities(response.content)

        Db.guardar_consulta(
            consulta=str(request.url_rule)[1:],
            tx=xml_ped,
            rx=response,
            ip=request.remote_addr
        )

        return response
