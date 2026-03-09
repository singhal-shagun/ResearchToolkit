from django.core.exceptions import ObjectDoesNotExist
from InfrastructureApp.db.models.ModelObjectUtils import copyInfrastructureModelFields
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils import timezone as djangoTimezonUtils


def loadUserEquivalences (apps):
    previousDBDictionaryIdentifier = "previousDB"
    UserEquivalencesModel = apps.get_model('ToolkitAdminApp', 'UserEquivalences')
    UserModel = get_user_model()

    users = UserModel.objects.all()

    userEquivalencesFromPreviousDB = UserEquivalencesModel.objects.using(previousDBDictionaryIdentifier).select_related(
        'referencedOriginalUser',
        'referencedEquivalentUser',
        )

    userEquivalencesForNewDB = []

    # Populating the database with the master data read from the previous database.
    if(len(userEquivalencesFromPreviousDB) > 0):
        mostRecentModifiedDateTimeInPreviousDB = datetime(year=1900, month=1, day=1, hour=0, minute=0)  # Since our software didn't exist on 1st Jan 1900, any recent edit would update it.
        if djangoTimezonUtils.is_naive(mostRecentModifiedDateTimeInPreviousDB):
            mostRecentModifiedDateTimeInPreviousDB = djangoTimezonUtils.make_aware(mostRecentModifiedDateTimeInPreviousDB)
        for userEquivalenceFromPreviousDB in userEquivalencesFromPreviousDB:
            if userEquivalenceFromPreviousDB.dbLastModifiedDateTime > mostRecentModifiedDateTimeInPreviousDB:
                mostRecentModifiedDateTimeInPreviousDB = userEquivalenceFromPreviousDB.dbLastModifiedDateTime

            userEquivalencesModelObject = UserEquivalencesModel()
            userEquivalencesModelObject.pk = None
        
            copyInfrastructureModelFields(
                incomingObjectFromOldDB = userEquivalenceFromPreviousDB, 
                objectDestinedToNewDB = userEquivalencesModelObject)

            userEquivalencesModelObject.referencedOriginalUser = users.get(username = userEquivalenceFromPreviousDB.referencedOriginalUser.username)
            userEquivalencesModelObject.referencedEquivalentUser = users.get(username = userEquivalenceFromPreviousDB.referencedEquivalentUser.username)
            
            userEquivalencesForNewDB.append(userEquivalencesModelObject)
    
        objs = UserEquivalencesModel.objects.bulk_create(userEquivalencesForNewDB)
        # mostRecentModifiedDateTimeInNewB = objs.order_by()