from django.core import management
from django.apps import apps
from django.contrib.auth import get_user_model

class Command(management.base.BaseCommand):
    help = "Changes the 'modifiedBy' user for all instances of a model."

    # Define the named constants.
    TARGET_APP = 'target_app'
    TARGET_MODEL = 'target_model'
    TARGET_USERNAME = 'target_username'

    def add_arguments(self, parser):
        # Although I've added loc, it's not supposed to do much because Django Docs didn't have call to super()... they had some custom implementation.
        # See https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
        super().add_arguments(parser)

        # 

    def handle(self, *args, **options):
        # 1. Before running this command, 
        TargetModel = apps.get_model('PlanningDteApp', 'Runways')
        targetUserObject = get_user_model().objects.get(username = "opsuser1")

        modelInstances = TargetModel.objects.all()
        for modelInstance in modelInstances:
            modelInstance.modifiedBy = targetUserObject
            modelInstance.save()
