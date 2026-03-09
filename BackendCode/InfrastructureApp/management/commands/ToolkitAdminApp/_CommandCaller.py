from django.core import management
from django.apps import apps

from ._masterdata_000_UserGroupsAndUsers import loadUsers
from ._data_001_UserEquivalences import loadUserEquivalences
from ._data_002_InvalidLoginCounter import loadInvalidLoginCounters


class Command(management.base.BaseCommand):
    def handle(self, *args, **options):
        objectList = [loadUsers, 
                      loadUserEquivalences, 
                      loadInvalidLoginCounters,
                      ]

        for objectReference in objectList:
            try:
                #objectReference = loadHangars
                self.stdout.write(self.style.MIGRATE_LABEL("Running " + ".".join(objectReference.__module__.split(".")[-2:]) + "..."))
                objectReference(apps=apps)
                self.stdout.write(self.style.SUCCESS(f'SUCCESS'))
            except Exception as e:
                #raise management.base.CommandError(e)
                raise e
            
        

