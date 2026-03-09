from django.db import models
from django.contrib.auth import get_user_model
from InfrastructureApp.db.models import InfrastructureModel

# Create your models here.
class UserEquivalences(InfrastructureModel):
    # REFERENCE FIELD DEFINITIONS
    referencedOriginalUser = models.ForeignKey(get_user_model(),
                                               on_delete=models.RESTRICT,
                                               verbose_name="ORIGINAL USER",
                                               related_name='userEquivalencesReferencedOriginalUser',
                                               help_text=r"Select the user to whom the Equivalent User is to be equated to.")

    referencedEquivalentUser = models.ForeignKey(get_user_model(),
                                               on_delete=models.RESTRICT,
                                               verbose_name="EQUIVALENT USER",
                                               related_name='userEquivalencesReferencedEquivalentUser',
                                               help_text=r"Select the user who is to become equivalent to the original user. This user will henceforth have access to the objects created/modifed by the Original User.")

    # MODEL METHOD DEFINITIONS SECTION
    def __str__(self):
        return (self.referencedOriginalUser.username + " : " + self.referencedEquivalentUser.username)

    def clean (self):
        from django.core.exceptions import ValidationError
        if (self.referencedOriginalUser.id == self.referencedEquivalentUser.id):  #CHECK-: Both the users shouldn't be same.
            errorText = "Please choose different users."
            raise ValidationError(errorText)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name="User Equivalence"
        verbose_name_plural="User Equivalences"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'referencedOriginalUser', 
                    'referencedEquivalentUser',
                    ], 
                name='unique_OriginalUser_EquivalentUser_UserEquivalences_Relationship',
                )
            ]
    


