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


def run_command(command, arguments=None):
    to_run = [command]
    if arguments:
        to_run += arguments
    try:
        result = subprocess.run(to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.returncode, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e) + "\n\n" + e.stderr.strip()
