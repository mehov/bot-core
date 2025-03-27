import importlib
import os
import telegram


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


async def detect_register_commands(subfolder, application):
    commands = [
        os.path.splitext(f)[0] for f in os.listdir(f'./{subfolder}')
        if os.path.splitext(f)[0].isidentifier() and not f.startswith('__')
    ]
    for command in commands:
        handler = None
        module = importlib.import_module(f"{subfolder}.{command}")
        camel_case = ''.join(word.capitalize() for word in command.split('_'))
        if hasattr(module, camel_case + 'Conversation'):
            command_ref = getattr(module, camel_case + 'Conversation')
            instance = command_ref()
            handler = instance.get_handler()
        if hasattr(module, camel_case + 'Command'):
            command_ref = getattr(module, camel_case + 'Command')
            instance = command_ref()
            handler = instance.get_handler()
        if handler is not None:
            application.add_handler(handler)
    # Add menu buttons
    commands = [telegram.BotCommand(command, command) for command in commands]
    await application.bot.set_chat_menu_button(menu_button=telegram.MenuButtonCommands())
    await application.bot.set_my_commands(commands)


