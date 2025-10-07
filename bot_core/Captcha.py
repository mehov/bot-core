from urllib.parse import urlencode
from flask import request, render_template, Blueprint
from jinja2 import ChoiceLoader, FileSystemLoader
import bot_core
import importlib
import json
import os

class Captcha:

    def __init__(self, captcha_key, user_id, credentials_id):
        """Start a new CAPTCHA handler where we expect to hit upstream challenge

        Arguments:
        captcha_key  unique key describing where and what we did to hit challenge
        user_id  whose requests got hit with CAPTCHA
        credentials_id  specific set used when hit with CAPTCHA
        """
        self.captcha_key = captcha_key
        self.user_id = user_id
        self.credentials_id = credentials_id

    def challenge_id(self):
        return f'{self.captcha_key}-{self.user_id}-{self.credentials_id}'

    @staticmethod
    def challenge_path(id):
        return f'/tmp/captcha-challenge-{id}'

    def is_pending(self):
        challenge_id = self.challenge_id()
        challenge_path = Captcha.challenge_path(challenge_id)
        return os.path.exists(challenge_path)

    def challenge(self, provider, captcha_url, challenge=None, user_agent=None):
        """Convenience function to return URL where we re-serve the CAPTCHA

        Arguments:
        provider  'datadome'
        captcha_url  CAPTCHA URL to re-serve through our proxy
        challenge  HTML code for CAPTCHA page (e.g. Cloudflare)
        user_agent  original user agent, use when proxying CAPTCHA requests
        """
        challenge_id = self.challenge_id()
        challenge_path = Captcha.challenge_path(challenge_id)
        with open(challenge_path, 'w') as f:
            f.write(challenge or '')
        metadata = {
            'captcha_key': self.captcha_key,
            'user_id': self.user_id,
            'credentials_id': self.credentials_id,
            'provider': provider,
            'captcha_url': captcha_url,
        }
        if user_agent:
            metadata['user_agent'] = user_agent
        with open(challenge_path + '.json', 'w') as f:
            json.dump(metadata, f)
        return bot_core.utils.app_url()+'/captcha?'+urlencode({'challenge_id': challenge_id})

    @staticmethod
    def read_challenge(challenge_id):
        challenge_path = Captcha.challenge_path(challenge_id)
        if not os.path.exists(challenge_path):
            return 'Provided challenge_id is not valid', None, None
        if not os.path.exists(challenge_path + '.json'):
            return 'Challenge metadata missing', None, None
        with open(challenge_path) as f:
            challenge = f.read()
        # Read challenge metadata into dict
        metadata = json.load(open(challenge_path + '.json'))
        return None, challenge, metadata

    @staticmethod
    async def captcha_routes(flask_app, telegram_app):
        # Path to bot_core root containing /static and /templates
        bot_core_path = os.path.dirname(os.path.abspath(bot_core.__file__))
        print('\n\nDEBUG bot_core_path: ', bot_core_path)
        # Tell Flask to look for templates in bot_core/templates
        flask_app.jinja_loader = ChoiceLoader([
            flask_app.jinja_loader,  # keep default template location
            FileSystemLoader(os.path.join(bot_core_path, 'templates')),  # add bot_core templates
        ])
        print('\n\nDEBUG flask_app.jinja_loader.loaders: ', [l.searchpath for l in flask_app.jinja_loader.loaders if isinstance(l, FileSystemLoader)])
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
            challenge_id = request.args.get('challenge_id')
            error, challenge, metadata = Captcha.read_challenge(challenge_id)
            if error:
                return error, 500
            return render_template(
                'captcha.html',
                challenge_id = challenge_id,
                metadata = metadata,
                iframe_src = '/captcha-challenge?'+urlencode({'challenge_id': challenge_id})
            )
        # Define Flask route used as our-origin iframe SRC where we serve CAPTCHA challenge code
        @flask_app.route('/captcha-challenge', methods=['GET'])
        def captcha_challenge_route():
            from flask import redirect
            challenge_id = request.args.get('challenge_id')
            error, challenge, metadata = Captcha.read_challenge(challenge_id)
            if error:
                return error, 500
            if len(challenge) == 0 & metadata.get('captcha_url').startswith('http'):
                return redirect(bot_core.Proxy().our_url(url=metadata.get('captcha_url'), user_agent=metadata.get('user_agent')), code=301)
            return challenge.encode('utf-8'), 200
        # Define Flask route where we save the CAPTCHA result for given user_id and provider
        @flask_app.route('/captcha-result', methods=['POST'])
        def captcha_result_route():
            data = request.get_data(as_text=True)
            if not data:
                return "Invalid or missing request data", 400
            provider_name = request.headers.get('X-Provider')
            if not provider_name:
                return "Missing 'X-Provider'", 400
            captcha_key = request.headers.get('X-Captcha-Key')
            if not captcha_key:
                return "Missing 'X-Captcha-Key'", 400
            challenge_id = request.headers.get('X-Challenge-Id')
            if not challenge_id:
                return "Missing 'X-Challenge-Id'", 400
            user_id = request.headers.get('X-User-Id')
            if not user_id:
                return "Missing 'X-User-Id'", 400
            credentials_id = request.headers.get('X-Credentials-Id')
            if not credentials_id:
                return "Missing 'X-Credentials-Id'", 400
            provider_module = importlib.import_module(f"bot_core.captcha_providers.{provider_name}")
            provider_reference = getattr(provider_module, provider_name)
            provider = provider_reference(captcha_key=captcha_key, user_id=user_id, credentials_id=credentials_id)
            response = provider.receive_captcha_response(data)
            if response.status_code == 200:
                challenge_path = Captcha.challenge_path(challenge_id)
                if os.path.exists(challenge_path):
                    os.remove(challenge_path)
                if os.path.exists(challenge_path + '.json'):
                    os.remove(challenge_path + '.json')
            return response

