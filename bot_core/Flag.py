import os
from .utils import app_identifier


class Flag:

    def __init__(self):
        self.prefix = app_identifier()

    def path(self, flag_id):
        return f"/tmp/{self.prefix}-{flag_id}.flag"

    def check(self, flag_id):
        path = self.path(flag_id)
        return os.path.exists(path)

    def set(self, flag_id, value=""):
        path = self.path(flag_id)
        with open(path, 'w') as handle:
            handle.write(str(value))

    def get(self, flag_id):
        path = self.path(flag_id)
        if not os.path.exists(path):
            return None
        handle = open(path, 'r')
        contents = handle.read()
        handle.close()
        return contents

    def mtime(self, flag_id):
        path = self.path(flag_id)
        if not os.path.exists(path):
            return None
        return os.path.getmtime(path)

    def remove(self, flag_id):
        path = self.path(flag_id)
        if os.path.exists(path):
            os.remove(path)
