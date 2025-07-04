from . import BaseCommand
from bot_core import Config
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


config = Config()


class StartCommand(BaseCommand):

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_data = update.message.from_user
        config.new_user(user_data.id, {
            'first_name': user_data.first_name,
            'language_code': user_data.language_code,
            'username': user_data.username,
        })
        await update.message.reply_text(f"Hello {user_data.first_name}! You can start using the bot now.")

    def get_handler(self):
        return CommandHandler('start', self.start_command)
