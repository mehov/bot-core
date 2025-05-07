import bot_core.utils
from . import BaseCommand
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


class UptimeCommand(BaseCommand):
    """Report bot status and uptime"""

    async def uptime_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        report = {
            'uptime': bot_core.utils.run_command('uptime')[1],
            'since': bot_core.utils.run_command('uptime', ['-s'])[1],
            'version': bot_core.utils.commit_id(),
            'message': bot_core.utils.commit_message(),
        }
        reply = ''
        for key, value in report.items():
            reply += f'<b>{key}</b><pre>{value}</pre>'
        await update.message.reply_text(reply, parse_mode='HTML')

    def get_handler(self):
        return CommandHandler('uptime', self.uptime_command)
