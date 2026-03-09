from django.db import models
from django.contrib.auth import get_user_model
from InfrastructureApp.db.models import InfrastructureModel
from django.core.validators import MaxValueValidator


class InvalidLoginCounter(InfrastructureModel):
    # REFERENCE FIELD DEFINITIONS
    parentUser = models.OneToOneField(get_user_model(),
                                      on_delete=models.RESTRICT,
                                      verbose_name="USER",
                                      related_name='invalidLoginCounterReferencedUser',
                                      help_text=r"Select the user for which Invalid Login Counter is to be set.")
    

    # MODEL FIELD DEFINITIONS
    invalidLoginCounter = models.PositiveSmallIntegerField(r"INVALID LOGIN COUNTER",
                                                           null=False,
                                                           blank=False,
                                                           unique=False,
                                                           default=0,
                                                           validators=[MaxValueValidator(limit_value = 5)],
                                                           help_text=r"Number of invalid login attempts (max 5).")
    

    # MODEL METHOD DEFINITIONS SECTION
    def __str__(self):
        return self.parentUser.username

    def clean (self):
        super().clean()


    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


    # MODEL CLASS META
    class Meta:
        ordering = ['parentUser',]
        verbose_name="Invalid Login Counter"
        verbose_name_plural="Invalid Login Counters"