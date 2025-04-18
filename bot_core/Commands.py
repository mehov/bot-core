import importlib
import os
import telegram


class Commands:

    def __init__(self, application):
        self.application = application
        self.menu_buttons = []

    def scan_dir(self, path):
        commands = [
            os.path.splitext(f)[0] for f in os.listdir(path)
            if os.path.splitext(f)[0].isidentifier() and not f.startswith('__')
        ]
        return commands

    async def register(self, path, module_name=None):
        """
        Registers all Commands and Conversations found in path with Telegram
        (Conversations have multiple steps as opposed to Commands)
        :param path: directory to scan for files
        :return: None
        """
        if not module_name:
            module_name = os.path.basename(path)  # last piece in path
        file_names = self.scan_dir(path)  # scan this path for files
        for file_name in file_names:
            handler = None  # default to None
            # First, import the file
            module = importlib.import_module(f"{module_name}.{file_name}")
            # Convert file_name to FileName
            camel_case = ''.join(word.capitalize() for word in file_name.split('_'))
            # If file_name contains a Conversation (multiple step interaction)
            if hasattr(module, camel_case + 'Conversation'):
                command_ref = getattr(module, camel_case + 'Conversation')
                instance = command_ref()
                handler = instance.get_handler()  # get the handler
            # If file_name contains a Command (simple one-step interaction)
            if hasattr(module, camel_case + 'Command'):
                command_ref = getattr(module, camel_case + 'Command')
                instance = command_ref()
                handler = instance.get_handler()  # get the handler
            # If we do have a handler after all, register it with Telegram
            if handler is not None:
                self.application.add_handler(handler)
            else:
                print(f'Handler for {file_name}/{camel_case} is None')
        # Add menu buttons
        self.menu_buttons += [telegram.BotCommand(name, 'Run /' + name) for name in file_names]

    async def register_core(self):
        await self.register(os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands')), 'bot_core.commands')

    async def save_menu_buttons(self):
        await self.application.bot.set_chat_menu_button(menu_button=telegram.MenuButtonCommands())
        await self.application.bot.set_my_commands(self.menu_buttons)
