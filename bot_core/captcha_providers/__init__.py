class BaseProvider:

    def __init__(self, user_id, credentials_id=None):
        self.user_id = user_id
        self.credentials_id = credentials_id

    def receive_captcha_response(self, data):
        return None
