import os
import configparser
import json
from .utils import app_identifier


def write_config(path, config):
    with open(path, 'w') as configfile:
        config.write(configfile)


class Config:

    def __init__(self, user_id=None):
        # Placeholders
        self.path = None # Shared app INI
        self.cache = {}
        self.config = configparser.ConfigParser()
        # If working with a specific user
        self.user_id = user_id
        # Directory where individual user INIs are stored
        self.user_dir = os.getenv('HOME') + '/' + app_identifier()
        # Make sure user_dir exists
        os.makedirs(self.user_dir, exist_ok=True)
        # Read and cache all INIs
        self.read()

    def list_user_ids(self):
        user_ids = [
            os.path.splitext(f)[0][len('USER'):] for f in os.listdir(self.user_dir)
            if os.path.splitext(f)[0].isidentifier() and not f.startswith('__')
        ]
        return user_ids

    def read(self):
        self.cache = {}
        self.path = os.path.dirname(os.path.dirname(__file__)) + "/config.ini"
        paths = [self.path] + [f'{self.user_dir}/USER{id}.ini' for id in self.list_user_ids()]
        self.config.read(paths)
        for section in self.config.sections():
            for (key, value) in self.config.items(section):
                self.cache[f'{section}_{key}'.upper()] = value

    def user_config(self, user_id=None):
        if not user_id:
            user_id = self.user_id
        section_name = f'USER{user_id}'
        if not self.config.has_section(section_name):
            return None
        return self.config.items(section_name)

    def get(self, name):
        # Make sure name is all uppercase
        name = name.upper()
        # Replace USER placeholder with actual USER_ID
        if name.split('_')[0] == 'USER' and self.user_id is not None:
            name = 'USER' + str(self.user_id) + name[len('USER'):]
        # Check environment first
        if name in os.environ:
            return os.getenv(name)
        # Return value from cached configs
        if name not in self.cache:
            return None
        return self.cache[name]

    def set(self, name, value):
        # Make sure name is all uppercase
        name = name.upper()
        # Make sure dict values are flattened to a valid JSON string
        if isinstance(value, dict):
            value = json.dumps(value)
        # Cache in environment
        os.environ[name] = value
        # Proceed writing to INI
        section = name.split('_')[0]
        key = name[len(section) + 1:]
        # Determine if writing to shared or user specific INI
        if section == 'USER' and self.user_id is not None:
            path = f'{self.user_dir}/USER{self.user_id}.ini'
            section = f'USER{self.user_id}'
        else:
            path = self.path
        print(path)
        # Read said INI
        temp_config = configparser.ConfigParser()
        temp_config.read(path)
        # Add section if needed
        if not temp_config.has_section(section):
            temp_config.add_section(section)
        # Set the value
        temp_config.set(section, key, value)
        # Finally, write the actual INI file
        write_config(path, temp_config)
        self.read()

    def new_user(self, user_id, user_data):
        self.user_id = user_id
        for key, value in user_data.items():
            self.set(f'USER_{key}', value)
        self.read()

