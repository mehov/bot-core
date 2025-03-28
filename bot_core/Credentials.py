from bot_core.Config import Config
from bot_core.Flag import Flag
import json


class Credentials:

    def __init__(self, user_id):
        self.user_id = user_id
        self.config = Config(user_id)

    def count(self):
        credentials = self.all()
        return len(credentials)

    def all(self):
        credentials = self.config.get('USER_ROTATING_CREDENTIALS')
        if not credentials:
            credentials = '[]'
        return json.loads(credentials)

    # adds a set of credentials to the config file
    def append(self, credential):
        credentials = self.all()
        credentials.append(credential)
        self.config.set('USER_ROTATING_CREDENTIALS', json.dumps(credentials))

    # gets credentials rotating them
    def get(self, force_use_credentials_id=False):
        # get all credentials
        credentials = self.all()
        if len(credentials) == 0:
            return None
        if force_use_credentials_id:
            credentials_id = force_use_credentials_id
        else:
            flag = Flag()
            # try reading the flag file, defaulting to ID = 0
            flag_id = f'credentials-{self.user_id}'
            flagged = flag.get(flag_id)
            if flagged:
                credentials_id = int(flagged)
                if (credentials_id + 1) < len(credentials):  # increment the ID, if we have more to go through
                    credentials_id = credentials_id + 1
                else:  # or go back to the start
                    credentials_id = 0
            else:
                credentials_id = 0
            # store the ID we're using
            flag.set(flag_id, credentials_id)
        # return the credentials set we obtained
        return credentials[credentials_id]

    # removes a set of credentials from the config file
    def discard(self, credential):
        new_credentials = []
        credentials = self.all()
        for c in credentials:
            if not c['access_token'] == credential['access_token']:
                new_credentials.append(c)
        self.config.set('USER_ROTATING_CREDENTIALS', json.dumps(new_credentials))
