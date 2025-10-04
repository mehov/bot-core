import datetime
from . import Captcha, Config, Proxy
from .utils import app_identifier
from flask import jsonify, request
from telegram import Update


config = Config()


class Routes:

    def __init__(self, flask_app, telegram_app):
        self.flask_app = flask_app
        self.telegram_app = telegram_app

    async def register_core(self):
        """
        Register routes provided by the core
        :return: None
        """
        # Dict of route names and their handler classes
        # Make sure static method exists in handler class with respective route name
        handlers = {
            'home': Routes,
            'webhook_endpoint': Routes,
            'proxy_routes': Proxy,
            'captcha_routes': Captcha,
        }
        for name, handler_obj in handlers.items():
            # Skip if route has already been defined
            if name in self.flask_app.view_functions:
                continue
            # Search for method with route name in handler class
            handler = getattr(handler_obj, name, None)
            if handler:
                await handler(self.flask_app, self.telegram_app)

    @staticmethod
    async def home(flask_app, telegram_app):
        @flask_app.route('/')
        async def home():
            return jsonify(
                app_name=app_identifier(),
                route='home',
                now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ), 200

    @staticmethod
    async def webhook_endpoint(flask_app, telegram_app):
        # set webhook if HTTP_HOSTNAME present in environment
        hostname = config.get('HTTP_HOSTNAME')
        if hostname is None:
            return

        # Do not pass custom port we may be using to Telegram
        # "webhook can be set up only on ports 80, 88, 443 or 8443"
        webhook_url = f"https://{hostname}/webhook-endpoint"
        print(f"Setting webhook URL to: {webhook_url}")
        await telegram_app.bot.set_webhook(webhook_url)

        @flask_app.route('/webhook-endpoint', methods=['POST'])
        async def webhook_endpoint():
            update = Update.de_json(request.get_json(), telegram_app.bot)
            await telegram_app.process_update(update)
            return jsonify(
                status='OK',
            ), 200
