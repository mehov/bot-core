import subprocess
from . import BaseCommand
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


def run_command(command, arguments=None):
    to_run = [command]
    if arguments:
        to_run += arguments
    try:
        result = subprocess.run(to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return str(e) + "\n\n" + e.stderr.strip()


class UptimeCommand(BaseCommand):
    """Report bot status and uptime"""

    async def uptime_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        reply = run_command('uptime')
        await update.message.reply_text(reply)

    def get_handler(self):
        return CommandHandler('uptime', self.uptime_command)
