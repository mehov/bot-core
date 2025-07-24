import os
import subprocess


def app_identifier() -> str:
    for candidate in [
        'APP_NAME',
        'SERVICE_NAME',
        'WEBSITE_SITE_NAME',  # Azure Web App Service
        'WEBSITE_DEPLOYMENT_ID',  # Azure Web App Service
        'APPLICATION_ID',  # Google App Engine
    ]:
        value = os.getenv(candidate)
        if value:
            return value.encode('ascii', 'ignore').decode().lower()
    return 'bot'


def app_url() -> str:
    env_port = os.getenv('HTTP_PORT')
    return '//' + (os.getenv('HTTP_HOST') or '127.0.0.1') + (f':{env_port}' if env_port else '')


def run_command(command, arguments=None):
    to_run = [command]
    if arguments:
        to_run += arguments
    try:
        result = subprocess.run(to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.returncode, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e) + "\n\n" + e.stderr.strip()
    except FileNotFoundError as e:
        return 127, str(e)


def commit_id():
    result = run_command('git', ['rev-parse', '--short', 'HEAD'])
    if result[0] == 0:
        return result[1]
    return '?'


def commit_message():
    result = run_command('git', ['log', '-1', '--pretty=%B'])
    if result[0] == 0:
        return result[1]
    return '?'

