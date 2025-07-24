import json
from bot_core.captcha_providers import BaseProvider
from bot_core import Credentials


class datadome(BaseProvider):

    def receive_captcha_response(self, data):
        if not self.credentials_id:
            return "Invalid credentials_id", 400
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return "Invalid JSON data", 400
        obj = Credentials(self.user_id)
        all = obj.all()
        all[int(self.credentials_id)]['cookie'] = data['cookie']
        obj.set(all)
        return data, 200
