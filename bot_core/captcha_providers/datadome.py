import json
from flask import Response
from bot_core.captcha_providers import BaseProvider
from bot_core import Captcha
from bot_core import Credentials
from bot_core import utils


class datadome(BaseProvider):

    def receive_captcha_response(self, data):
        if not self.credentials_id:
            return Response('Invalid credentials_id', 400)
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return Response('Invalid JSON data', 400)
        if data['view'] == 'captcha':
            new_captcha = Captcha(captcha_key=self.captcha_key, user_id=self.user_id, credentials_id=self.credentials_id)
            challenge_id = new_captcha.challenge_id()
            error, challenge, metadata = Captcha.read_challenge(challenge_id)
            print(f'\n\nCaptcha.read_challenge({challenge_id})\nError: {error}\nChallenge: {challenge}\nMetadata:\n{json.dumps(metadata, indent=4)}')
            if error:
                return Response(error, 500)
            # Trigger saving new captcha URL
            new_captcha.challenge(provider='datadome', captcha_url=data['url'], user_agent=metadata.get('user_agent'))
            # Start building Response object
            # Pass cookie we received - so that it's used for the new captcha
            cookie = data['cookie']
            # Edit cookie Domain
            import re
            cookie = re.sub(r'Domain=[^;]+', f'Domain=.{utils.app_host()}', cookie)
            return Response(data, 303, headers={'Set-Cookie': cookie})
        obj = Credentials(self.user_id)
        all = obj.all()
        all[int(self.credentials_id)]['cookie'] = data['cookie']
        obj.set(all)
        return Response(data, 200)
