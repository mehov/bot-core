import datetime
from . import Config
from .utils import app_identifier
from flask import jsonify, request
from telegram import Update


config = Config()


class Routes:

    def __init__(self, flask_app, telegram_app):
        self.flask_app = flask_app
        self.telegram_app = telegram_app

    async def register_core(self):
        for f in ['home', 'webhook_endpoint']:
            if f not in self.flask_app.view_functions:
                handler = getattr(self, f, None)
                if handler:
                    await handler()

    async def home(self):
        @self.flask_app.route('/')
        async def home():
            return jsonify(
                app_name=app_identifier(),
                route='home',
                now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ), 200

    async def webhook_endpoint(self):
        # set webhook if HTTP_HOSTNAME present in environment
        hostname = config.get('HTTP_HOSTNAME')
        if hostname is None:
            return

        # Do not pass custom port we may be using to Telegram
        # "webhook can be set up only on ports 80, 88, 443 or 8443"
        webhook_url = f"https://{hostname}/webhook-endpoint"
        print(f"Setting webhook URL to: {webhook_url}")
        await self.telegram_app.bot.set_webhook(webhook_url)

        @self.flask_app.route('/webhook-endpoint', methods=['POST'])
        async def webhook_endpoint():
            update = Update.de_json(request.get_json(), self.telegram_app.bot)
            await self.telegram_app.process_update(update)
            return jsonify(
                status='OK',
            ), 200
