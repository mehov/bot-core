import json
from bot_core.captcha_providers import BaseProvider
from bot_core import Captcha
from bot_core import Credentials


class datadome(BaseProvider):

    def receive_captcha_response(self, data):
        if not self.credentials_id:
            return "Invalid credentials_id", 400
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return "Invalid JSON data", 400
        if data['view'] == 'captcha':
            new_captcha = Captcha(captcha_key=self.captcha_key, user_id=self.user_id, credentials_id=self.credentials_id)
            challenge_id = new_captcha.challenge_id()
            error, challenge, metadata = Captcha.read_challenge(challenge_id)
            print(f'\n\nCaptcha.read_challenge({challenge_id})\nError: {error}\nChallenge: {challenge}\nMetadata:\n{json.dumps(metadata, indent=4)}')
            if error:
                return error, 500
            # Trigger saving new captcha URL
            new_captcha.challenge(provider='datadome', captcha_url=data['url'], user_agent=metadata.user_agent)
            return data, 303
        obj = Credentials(self.user_id)
        all = obj.all()
        all[int(self.credentials_id)]['cookie'] = data['cookie']
        obj.set(all)
        return data, 200
