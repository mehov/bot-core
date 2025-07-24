from urllib.parse import urlencode
from flask import request, render_template, Blueprint
from jinja2 import ChoiceLoader, FileSystemLoader
import bot_core
import importlib
import os

class Captcha:

    def our_url(self, user_id, credentials_id, provider, captcha_url, user_agent=None):
        """Convenience function to return URL where we re-serve the CAPTCHA

        Arguments:
        user_id  whose requests got hit with CAPTCHA
        credentials_id  specific set used when hit with CAPTCHA
        provider
        captcha_url
        user_agent  original user agent, use when proxying CAPTCHA requests
        """
        query = {
            'user_id': user_id,
            'credentials_id': credentials_id,
            'provider': provider,
            'captcha_url': captcha_url,
        }
        if user_agent:
            query['user_agent'] = user_agent
        return bot_core.utils.app_url()+'/captcha?'+urlencode(query)

    async def captcha_routes(self, flask_app, telegram_app):
        # Path to bot_core root containing /static and /templates
        bot_core_path = os.path.dirname(os.path.dirname(os.path.abspath(bot_core.__file__)))
        # Tell Flask to look for templates in bot_core/templates
        flask_app.jinja_loader = ChoiceLoader([
            flask_app.jinja_loader,  # keep default template location
            FileSystemLoader(os.path.join(bot_core_path, 'templates')),  # add bot_core templates
        ])
        # Tell Flask to look for static files in bot_core/static
        flask_app.register_blueprint(Blueprint(
            'bot_core',
            __name__,
            static_folder=os.path.join(bot_core_path, 'static'),
            static_url_path='/bot_core_static'
        ))
        # Define Flask route where we re-serve the CAPTCHA we received
        @flask_app.route('/captcha')
        def captcha_serve_route():
            captcha_url = request.args.get('captcha_url')
            user_agent = request.args.get('user_agent')
            return render_template(
                'captcha.html',
                provider = request.args.get('provider'),
                user_id = request.args.get('user_id'),
                credentials_id = request.args.get('credentials_id'),
                captcha_url = captcha_url,
                user_agent = user_agent,
                proxy_url = bot_core.Proxy().our_url(url=captcha_url, user_agent=user_agent)
            )
        # Define Flask route where we save the CAPTCHA result for given user_id and provider
        @flask_app.route('/captcha-result', methods=['POST'])
        def captcha_result_route():
            data = request.get_data(as_text=True)
            if not data:
                return "Invalid or missing request data", 400
            provider_name = request.headers.get('X-Provider')
            if not provider_name:
                return "Missing 'X-Provider'", 400
            user_id = request.headers.get('X-User-Id')
            if not user_id:
                return "Missing 'X-User-Id'", 400
            credentials_id = request.headers.get('X-Credentials-Id')
            if not credentials_id:
                return "Missing 'X-Credentials-Id'", 400
            provider_module = importlib.import_module(f"bot_core.captcha_providers.{provider_name}")
            provider_reference = getattr(provider_module, provider_name)
            provider = provider_reference(user_id=user_id, credentials_id=credentials_id)
            return provider.receive_captcha_response(data)

