
from types import SimpleNamespace
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ...constants import Users


def setDefaultCreatedByModifiedByUsers(obj, username = None, userObject = None):
    """
    This function sets the 'createdBy' and 'modifiedBy' fields of the provided object to the default user. 
    If a user object is provided, it will be used as the default user. 
    Else, the user object corresponding to the provided username will be retrieved from the database.
        - If username is not provided, the root user will be used as the default.

    :param obj: The object for which to set the default users.
    :param username: Optional. The username of the user to use as the default. If not provided, the root user will be used.
    :param userObject: Optional. The user object to use as the default. If not provided, the user object corresponding to the provided username will be retrieved.

    :return: The object with the 'createdBy' and 'modifiedBy' fields set to the default user.
    """
    if (userObject is None):
        if (username is None):
            username = Users.RootUser.username
        userObject = get_user_model().objects.get(username = username)
    obj.createdBy_id = userObject.id
    obj.modifiedBy_id = userObject.id
    return obj


def changeModifiedByUser(obj, username = None, userObject = None):
    """
    This function changes the 'modifiedBy' field of the provided object to the default user. 
    If a user object is provided, it will be used as the default user. 
    Else, the user object corresponding to the provided username will be retrieved from the database.
        - If username is not provided, the root user will be used as the default.

    :param obj: The object for which the 'modifiedBy' attribute is to be changed.
    :param username: Optional. The username of the user. If not provided, the root user will be used.
    :param userObject: Optional. The user object. If not provided, the user object corresponding to the provided username will be retrieved.

    :return: The object with the changed 'modifiedBy' field.
    """
    if (userObject is None):
        if (username is None):
            username = Users.RootUser.username
        userObject = get_user_model().objects.get(username = username)
    obj.modifiedBy_id = userObject.id
    return obj


def copyInfrastructureModelFields(incomingObjectFromOldDB, objectDestinedToNewDB, previousDBDictionaryIdentifier=None):
    if isinstance(incomingObjectFromOldDB, dict):
        """
        This is the case when incomingObjectFromOldDB will be a dict-type object because the data is being fetched using raw query.
        So, you will have to fetch the createdBy and modifiedBy from the previous database.
        """
        if previousDBDictionaryIdentifier is None:
            raise Exception("The 'previousDBDictionaryIdentifier' parameter is mandatory when the 'objectDestinedToNewDB' is a dict-type object.")
        
        # 1. Fetch createdBy user and modifiedBy user from previous database.
        createdByUserFromPreviousDatabase = get_user_model().objects.using(previousDBDictionaryIdentifier).get(id = incomingObjectFromOldDB["createdBy_id"])
        modifiedByUserFromPreviousDatabase = get_user_model().objects.using(previousDBDictionaryIdentifier).get(id = incomingObjectFromOldDB["modifiedBy_id"])

        # 2. Find the corresponding users in the new database and associate them with the objectDestinedToNewDB.
        objectDestinedToNewDB.createdBy_id = get_user_model().objects.get(username = createdByUserFromPreviousDatabase.username).id
        objectDestinedToNewDB.modifiedBy_id = get_user_model().objects.get(username = modifiedByUserFromPreviousDatabase.username).id

        # 3. Copy the dbEntryCreationDateTime and dbLastModifiedDateTime as is.
        objectDestinedToNewDB.dbEntryCreationDateTime = incomingObjectFromOldDB["dbEntryCreationDateTime"]
        objectDestinedToNewDB.dbLastModifiedDateTime = incomingObjectFromOldDB["dbLastModifiedDateTime"]
    # elif isinstance(incomingObjectFromOldDB, ModelSchema):
    elif isinstance(incomingObjectFromOldDB, SimpleNamespace):
        """
        This is the case when incomingObjectFromOldDB has been created using Django-Ninja's ModelSchema.
        """
        if previousDBDictionaryIdentifier is None:
            raise Exception("The 'previousDBDictionaryIdentifier' parameter is mandatory when the 'objectDestinedToNewDB' is a dict-type object.")
        
        # 1. Fetch createdBy user and modifiedBy user from previous database.
        createdByUserFromPreviousDatabase = get_user_model().objects.using(previousDBDictionaryIdentifier).get(id = incomingObjectFromOldDB.createdBy_id)
        modifiedByUserFromPreviousDatabase = get_user_model().objects.using(previousDBDictionaryIdentifier).get(id = incomingObjectFromOldDB.modifiedBy_id)

        # 2. Find the corresponding users in the new database and associate them with the objectDestinedToNewDB.
        objectDestinedToNewDB.createdBy_id = get_user_model().objects.get(username = createdByUserFromPreviousDatabase.username).id
        objectDestinedToNewDB.modifiedBy_id = get_user_model().objects.get(username = modifiedByUserFromPreviousDatabase.username).id

        # 3. Copy the dbEntryCreationDateTime and dbLastModifiedDateTime as is.
        objectDestinedToNewDB.dbEntryCreationDateTime = incomingObjectFromOldDB.dbEntryCreationDateTime
        objectDestinedToNewDB.dbLastModifiedDateTime = incomingObjectFromOldDB.dbLastModifiedDateTime
    else:
        """"
        This is the case when incomingObjectFromOldDB will be an object instance created by Django's ORM.
        """
        objectDestinedToNewDB.createdBy_id = get_user_model().objects.get(username = incomingObjectFromOldDB.createdBy.username).id
        objectDestinedToNewDB.modifiedBy_id = get_user_model().objects.get(username = incomingObjectFromOldDB.modifiedBy.username).id
        objectDestinedToNewDB.dbEntryCreationDateTime = incomingObjectFromOldDB.dbEntryCreationDateTime
        objectDestinedToNewDB.dbLastModifiedDateTime = incomingObjectFromOldDB.dbLastModifiedDateTime



def getKeyFromDisplayedChoiceValue(displayedChoiceValue, choicesList):
    for choice in choicesList:  # Iterate through the choice list to find the matching key.
        if choice[1] == displayedChoiceValue:
            return choice[0]
    raise ValidationError("Choice value " + displayedChoiceValue + " not found in choices list.")   # Raise an error if the key is not found.