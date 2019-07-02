# -*- coding: utf-8 -*-

import re
from requests import Session, Request, Response
from requests.auth import HTTPProxyAuth
from base64 import b64decode
from app import app


class Util:

    @staticmethod
    def check_parameters(names, params):
        for param in names:
            if param not in params:
                raise Exception(u'Parámetro requerido: {}'.format(param))

    @staticmethod
    def format_replaceXMLEntities(xml):
        for k, v in [('&lt;', '<'), ('&gt;', '>')]:
            xml = xml.replace(k, v)

        return xml

    @staticmethod
    def format_removeXMLPrefixes(xml):
        xml = re.sub(r'(</?)[\w]+:', '\\1', xml)
        xml = re.sub(r'(</?[\w]+\s)([\w]+:)([\w]+)', '\\1\\3', xml)
        return xml

    @staticmethod
    def format_removeXMLNodeNamespace(value):
        return re.sub(r'\{[a-z.:/]+\}', '', value)

    @staticmethod
    def cursor_to_dict(cursor):
        columns = [i[0] for i in cursor.description]
        return [dict(zip(columns, row)) for row in cursor]

    @staticmethod
    def get_proxies():
        proxies = {}

        if app.config['PROXY_HOST']:
            for protocol in ('http', 'https'):
                proxies.update({
                    protocol: (
                        'http://{}:{}@{}:{}'.format(
                            app.config['PROXY_USER'],
                            b64decode(app.config['PROXY_PASSWORD']),
                            app.config['PROXY_HOST'],
                            str(app.config['PROXY_PORT'])
                        )
                    )
                })

        return proxies

    @staticmethod
    def get_proxy_auth():
        if app.config['PROXY_USER']:
            return HTTPProxyAuth(app.config['PROXY_USER'], b64decode(app.config['PROXY_PASSWORD']))
        else:
            return None

    @staticmethod
    def get_http_request(url, payload, method='POST', headers=None, use_proxy=False, use_proxy_auth=False, trust_env=True):
        try:
            session = Session()
            session.trust_env = trust_env
            session.proxies = Util.get_proxies() if use_proxy else None
            session.auth = Util.get_proxy_auth() if use_proxy_auth else None

            request = Request(
                'POST' if method not in ('GET', 'POST') else method,
                url,
                data=payload if method == 'POST' else None,
                params=payload if method == 'GET' else None,
                headers=headers
            )

            prepped = request.prepare()

            response = session.send(
                prepped,
                timeout=app.config['HTTP_REQUESTS_TIMEOUT']
            )

            session.close()
        except Exception , e:
            response = Response()
            response.raise_for_status()
            return response, 'Error al realizar la consulta - Motivo: {}'.format(e.message)

        return response, None
