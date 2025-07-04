import bot_core
from . import BaseCommand
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


class MeCommand(BaseCommand):
    """Report current user data"""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        config = bot_core.Config(update.message.from_user.id)
        message = ''
        for key, value in config.user_config():
            message += f'<b>{key}</b><pre>{value}</pre>'
        await update.message.reply_text(message, parse_mode='HTML')

    def get_handler(self):
        return CommandHandler('me', self.handle)
