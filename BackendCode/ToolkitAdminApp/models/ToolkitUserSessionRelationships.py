from django.db import models
from InfrastructureApp.db.models import InfrastructureModel
from django.contrib.auth import get_user_model
# from django.contrib.sessions.models import Session
from importlib import import_module
from django.conf import settings

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from .SessionsModel import Sessions

class ToolkitUserSessionRelationships (InfrastructureModel):
    # REFERENCE FIELD DEFINITIONS
    parentUser = models.OneToOneField(get_user_model(),
                                          on_delete=models.RESTRICT,
                                          verbose_name="USER",
                                          related_name='toolkitUserSessionRelationshipsParentUser',
                                               help_text=r"Select the user.")
    
    # parentSession = models.OneToOneField(Session,
    # parentSession = models.OneToOneField(SessionStore.get_model_class(),
    parentSession = models.OneToOneField(Sessions,
                                      on_delete=models.CASCADE,
                                      verbose_name="SESSION",
                                      related_name='toolkitUserSessionRelationshipsParentSession',
                                      help_text=r"Select the Session.")


    # MODEL METHOD DEFINITIONS SECTION
    def __str__(self):
        return self.referencedUser.username
    
    def clean (self):
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    
    # MODEL META DEFINITION.
    class Meta:
        ordering = ['parentUser',]
        verbose_name="Toolkit User Session Relationship"
        verbose_name_plural="Toolkit User Session Relationships"