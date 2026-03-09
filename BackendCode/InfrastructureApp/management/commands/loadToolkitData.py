from django.core import management
from .ToolkitAdminApp import _CommandCaller as ToolkitAdminApp_CommandCaller

class Command(management.base.BaseCommand):
    help = "Loads data into the Database either from excel files or from previous database."

    def add_arguments(self, parser):
        # Although I've added loc, it's not supposed to do much because Django Docs didn't have call to super()... they had some custom implementation.
        # See https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
        super().add_arguments(parser)   

    def handle(self, *args, **options):
        commandObjectsList = [
            ToolkitAdminApp_CommandCaller,
            ]
        for commandObject in commandObjectsList:
            management.call_command(commandObject.Command())
