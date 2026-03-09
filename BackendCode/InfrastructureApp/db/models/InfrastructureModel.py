from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
#from django.core.validators import MinValueValidator, MaxValueValidator
#from django.core.exceptions import ValidationError, ObjectDoesNotExist

# Create your models here.

class InfrastructureModel(models.Model):
    # MASTER DATA SECTION
    #ENTRY_ACTIVE_YES_NO_CHOICES = (
    #    (True, 'Yes'),
    #    (False, 'No'))

    # FIELD DEFINITIONS SECTION
    #entryActiveYesNo = models.BooleanField(r"Is this database entry still active? (YES/NO)",
    #                                  null=False,
    #                                  blank=False,
    #                                  unique=False,
    #                                  choices=ENTRY_ACTIVE_YES_NO_CHOICES,
    #                                  help_text=r"Is this database entry still active? If it's been changed/modified to something else, mark this as False.")
    createdBy = models.ForeignKey (get_user_model(),
                                   on_delete=models.RESTRICT,
                                   verbose_name="CREATED BY (USER)",
                                   related_name="%(app_label)s%(class)sCreatedBy")

    dbEntryCreationDateTime=models.DateTimeField(r"Entry creation date-time",
                                     null=False,
                                     blank=False,
                                     #auto_now_add=True, #Commented because it doesn't allow for preservation of the data during database migration.
                                     default=timezone.now,
                                     help_text=r"This is the date-time when this entry was created. It's supposed to be system-generated and non-modifiable by any user.")
    
    modifiedBy = models.ForeignKey (get_user_model(),
                                   on_delete=models.RESTRICT,
                                   verbose_name="MODIFIED BY (USER)",
                                   related_name="%(app_label)s%(class)sModifiedBy")

    dbLastModifiedDateTime=models.DateTimeField(r"Last Modified date-time",
                                     null=False,
                                     blank=False,
                                     #auto_now=True, #Commented because it doesn't allow for preservation of the data during database migration, even though the docs say that it's not triggerred unless model's save() is called..
                                     default=timezone.now,
                                     help_text=r"This is the date-time when this entry was last modified. It's supposed to be system-generated and non-modifiable by any user.")
    
    # MODEL FUNCTION DEFINITIONS
    def __str__(self):
        return super().save()
    
    def clean (self):
        super().clean()
        # model-specific cleansing code goes here.

    def save(self, *args, **kwargs):
        self.clean()
        self.dbLastModifiedDateTime = timezone.now()
        # model-specific saving code goes here.
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        


