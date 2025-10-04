from urllib.parse import urlencode
from flask import request, Response
import bot_core
import requests


class Proxy:

    def our_url(self, url, user_agent=None):
        """Shorthand to generate URL to our endpoint proxying given URL for given user_agent

        Arguments:
            url: URL that needs to be proxied and contents retrieved
            user_agent: Force the requests library to use this HTTP User-Agent header
        """
        query = {'url': url}
        if user_agent:
            query['user_agent'] = user_agent
        return bot_core.utils.app_url()+'/proxy?'+urlencode(query)

    @staticmethod
    async def proxy_routes(flask_app, telegram_app):
        """Callback to be used in Routes.py"""
        @flask_app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
        def handle_proxy():
            """Handle requests coming to our proxy endpoint, perform actual proxying"""
            url = request.args.get('url')  # URL we need to get the contents from
            user_agent = request.args.get('user_agent')  # use this as HTTP User-Agent header
            referer = request.args.get('referer')  # use this as HTTP Referer header

            if not url:
                return "Missing 'url' parameter", 400

            try:
                # Copy headers, use custom User-Agent and Referer if provided
                headers = {
                    key: value
                    for key, value in request.headers
                    if key.lower() not in ('host', 'referer')  # clear; may set below
                }
                if user_agent:
                    headers['User-Agent'] = user_agent
                if referer:
                    headers['Referer'] = referer
                headers['Accept-Encoding'] = 'identity'

                # Forward received query params (excluding 'url', 'user_agent', 'referer' which are for proxy itself)
                forwarded_params = {k: v for k, v in request.args.items() if k not in ('url', 'user_agent', 'referer')}

                # Forward the original request using the same HTTP method
                resp = requests.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    params=forwarded_params,
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=False,
                )

                # Build our response with content from proxied response
                proxy_response = Response(
                    resp.content,
                    status=resp.status_code,
                    content_type=resp.headers.get('Content-Type', 'application/octet-stream')
                )

                # Optionally forward selected headers (e.g., set-cookie, content-disposition)
                hop_by_hop_headers = {'transfer-encoding', 'connection', 'keep-alive', 'proxy-authenticate',
                                      'proxy-authorization', 'te', 'trailers', 'upgrade', 'content-encoding'}
                for header, value in resp.headers.items():
                    if header.lower() not in hop_by_hop_headers:
                        proxy_response.headers[header] = value

                return proxy_response, resp.status_code

            except Exception as e:
                return f"Proxy error: {str(e)}", 500
