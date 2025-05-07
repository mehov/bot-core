import subprocess
from . import BaseCommand
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


class UptimeCommand(BaseCommand):
    """Report bot status and uptime"""

    async def uptime_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            result = subprocess.run(["uptime"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    check=True)
            reply = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            reply = e
        await update.message.reply_text(reply)

    def get_handler(self):
        return CommandHandler('uptime', self.uptime_command)
