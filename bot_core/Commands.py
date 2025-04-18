import importlib
import os
import telegram


class Commands:

    def __init__(self, application):
        self.application = application

    def scan_dir(self, path):
        commands = [
            os.path.splitext(f)[0] for f in os.listdir(path)
            if os.path.splitext(f)[0].isidentifier() and not f.startswith('__')
        ]
        return commands

    async def register(self, path):
        """
        Registers all Commands and Conversations found in path with Telegram
        (Conversations have multiple steps as opposed to Commands)
        :param path: directory to scan for files
        :return: None
        """
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
        # Add menu buttons
        buttons_list = [telegram.BotCommand(name, 'Run /' + name) for name in file_names]
        await self.application.bot.set_chat_menu_button(menu_button=telegram.MenuButtonCommands())
        await self.application.bot.set_my_commands(buttons_list)
