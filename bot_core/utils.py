import os


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
