from django.apps import apps
from django.db import connections
from InfrastructureApp.db.models.ModelObjectUtils import copyInfrastructureModelFields
from django.contrib.auth import get_user_model


def loadInvalidLoginCounters (apps):
    previousDBDictionaryIdentifier = "previousDB"
    InvalidLoginCounterModel = apps.get_model('ToolkitAdminApp', 'InvalidLoginCounter')
    UserModel = get_user_model()

    """
    1. Fetch the data for referenced fields from both new and previous database.
    """
    # 1.1. From the new database.
    users = UserModel.objects.all()

    # 1.2.From previous database.
    with connections[previousDBDictionaryIdentifier].cursor() as cursor:
        cursor.execute('SELECT * FROM public.auth_user ORDER BY id ASC')
        columnNames = [column[0] for column in cursor.description]
        usersFromPreviousDB = [dict(zip(columnNames, row)) for row in cursor.fetchall()]

    """
    2. Load from previous database the data for the model in question (i.e., the InvalidLoginCounter model).
       This is the actual data to be migrated to the new database.
    """
    with connections[previousDBDictionaryIdentifier].cursor() as cursor:
        cursor.execute('SELECT * FROM public."ToolkitAdminApp_invalidlogincounter" ORDER BY id ASC')
        columnNames = [column[0] for column in cursor.description]
        invalidLoginCountersFromPreviousDB = [dict(zip(columnNames, row)) for row in cursor.fetchall()]

    # Create a list of objects for the new database.
    invalidLoginCountersForNewDB = []

    for invalidLoginCounterFromPreviousDB in invalidLoginCountersFromPreviousDB:
        invalidLoginCounterForNewDB = InvalidLoginCounterModel()
        invalidLoginCounterForNewDB.pk = None

        copyInfrastructureModelFields(
            incomingObjectFromOldDB = invalidLoginCounterFromPreviousDB,
            objectDestinedToNewDB = invalidLoginCounterForNewDB,
            previousDBDictionaryIdentifier = previousDBDictionaryIdentifier
        )

        # 1. Copy the references for Reference Key fields.
        parentUserIDFromPreviousDB = invalidLoginCounterFromPreviousDB["parentUser_id"]
        parentUserFromPreviousDB = None
        for userFromPreviousDB in usersFromPreviousDB:
            if userFromPreviousDB['id'] == parentUserIDFromPreviousDB:
                parentUserFromPreviousDB = userFromPreviousDB
                break
        invalidLoginCounterForNewDB.parentUser_id = users.get(
            username = parentUserFromPreviousDB["username"],
            ).id
        
        # 2. Copy the data fields.
        invalidLoginCounterForNewDB.invalidLoginCounter = invalidLoginCounterFromPreviousDB["invalidLoginCounter"]
        
        invalidLoginCountersForNewDB.append(invalidLoginCounterForNewDB)

    objs = InvalidLoginCounterModel.objects.bulk_create(invalidLoginCountersForNewDB)