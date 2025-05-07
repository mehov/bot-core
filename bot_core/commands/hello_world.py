from . import BaseCommand
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


class HelloWorldCommand(BaseCommand):
    """Say hello"""

    async def hello_world_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text('Hello World!')

    def get_handler(self):
        return CommandHandler('hello_world', self.hello_world_command)
