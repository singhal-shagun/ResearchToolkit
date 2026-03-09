from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.core.exceptions import ObjectDoesNotExist


class SessionStore(DBStore):
    @classmethod
    def get_model_class(cls):
        from ToolkitAdminApp.models import Sessions
        return Sessions
    

    def cycle_key(self):
        """
        Calling super().cycle_key() will:
            1. Create a new session entry in the database with a new session_key, mapping the existing session data to the new session entry.
            2. Delete the session entry from the database corresponding to the old session key.
        We are overriding this method because ToolkitUserSessionRelationships model has a CASCADE relationship with session_key.
        Hence, when super().cycle_key() deleted the DB entry corresponding to the old session key, the corresponding ToolkitUserSessionRelationship is also deleted.
        Thus, this overridden method will do the following:
            1. Retrieve the ToolkitUserSessionRelationship data corresponding to the old session key (because otherwise, we won't know the userID we're working with) ;
            2. Call super().cycle_key();
            3. Create a new ToolkitUserSessionRelationship for the user with the new session key.
        """

        # 1. Retrieve the ToolkitUserSessionRelationship data corresponding to the old session key (because otherwise, we won't know the userID we're working with).
        try:
            from ToolkitAdminApp.models import ToolkitUserSessionRelationships
            toolkitUserSessionRelationship = ToolkitUserSessionRelationships.objects.get(parentSession_id = self.session_key)
        except ObjectDoesNotExist:
            toolkitUserSessionRelationship = None

        # 2. Call super().cycle_key().
        super().cycle_key()

        # 3. Create a new ToolkitUserSessionRelationship for the user with the new session key.
        if toolkitUserSessionRelationship is not None:
            toolkitUserSessionRelationship.parentSession_id = self.session_key
            toolkitUserSessionRelationship.save()
    