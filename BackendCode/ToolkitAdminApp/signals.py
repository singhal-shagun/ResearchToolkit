from .models import ToolkitUserSessionRelationships
# from django.contrib.sessions.models import Session
# from django.contrib.sessions.backends.db import SessionStore
from importlib import import_module
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from InfrastructureApp.db.models.ModelObjectUtils import setDefaultCreatedByModifiedByUsers

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

# SIGNAL RECEIVERS GO HERE.
def createUserSessionRelationshipUponLogin(sender, **kwargs):
    """
    django.contrib.auth.login() sends the `user_logged_in` signal as follows:
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    """

    request = kwargs['request']
    user = kwargs['user']

    # Step-1: Check if a session exists for the current user.
    try:
        toolkitUserSessionRelationship = ToolkitUserSessionRelationships.objects.get(parentUser_id=user.id)
        userPreviousSession = SessionStore(session_key = toolkitUserSessionRelationship.parentSession_id)
        toolkitUserSessionRelationship.delete()
        userPreviousSession.delete()
    except ObjectDoesNotExist:
        # Since there's no previous user-session relationship, we need not delete anything.
        pass

    # Step-2: Create a new user-session relationship.
    toolkitUserSessionRelationship = ToolkitUserSessionRelationships()
    setDefaultCreatedByModifiedByUsers(toolkitUserSessionRelationship)
    toolkitUserSessionRelationship.parentUser_id = user.pk
    toolkitUserSessionRelationship.parentSession_id = request.session.session_key
    toolkitUserSessionRelationship.save()


def deleteUserSessionRelationshipUponLogin(sender, **kwargs):
    """
    django.contrib.auth.logout() sends the `user_logged_out` signal as follows:
    user_logged_out.send(sender=user.__class__, request=request, user=user)

    [NOTES:] 
        1. Unless the user-session relationship is deleted, Django won't be able to log the user out.
        2. Django is able to flush the user session afterwards because django.contrib.auth.logout() sends the `user_logged_out` signal before trying to flush the user session.
    """
    user = kwargs['user']
    toolkitUserSessionRelationship = ToolkitUserSessionRelationships.objects.get(parentUser_id=user.id)
    toolkitUserSessionRelationship.delete()