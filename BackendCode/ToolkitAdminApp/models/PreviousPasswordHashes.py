from django.db import models
from django.contrib.auth import get_user_model
from InfrastructureApp.db.models import InfrastructureModel
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from InfrastructureApp.constants import Users
from django.utils.translation import gettext_lazy as _



# Create your models here.
class PreviousPasswordHashes(InfrastructureModel):
    # ERROR MESSAGES' DEFINITION.
    errorMessage = "Password matches one of the previous {N} passwords.".format(N = Users.PASSWORD_HISTORY_LENGTH)

    # REFERENCE FIELD DEFINITIONS
    referencedUser = models.ForeignKey(get_user_model(),
                                               on_delete=models.RESTRICT,
                                               verbose_name="REFERENCED USER",
                                               related_name='previousPasswordHashesReferencedUser',
                                               help_text=r"Select the user to whom the Equivalent User is to be equated to.")

    passwordHash = models.CharField(_("password"), max_length=128)  # Copied from https://github.com/django/django/blob/1ac397674b2f64d48e66502a20b9d9ca6bfb579a/django/contrib/auth/base_user.py#L59C63-L60C5

    # MODEL METHOD DEFINITIONS SECTION
    def __str__(self):
        return self.referencedUser.username

    def clean (self):
        super().clean()
        """
        CHECK-1: Ensure that the incoming password hash isn't same as the past N password hashes.
        CHECK-2: If it doesn't match the past N hashes, delete the oldest password hash if there are already N (current + (N-1)) previous) password hashes in the database to make space for the new password's hash.
        """
        # CHECK-1: Ensure that not more than N (current + (N-1)) previous) password hashes are stored in the database.
        try:
            PreviousPasswordHashes.objects.get(referencedUser_id = self.referencedUser.id, passwordHash = self.passwordHash)
            # If no exception raised, raise a validation error that the password matches the previous N passwords.
            ValidationError(self.errorMessage)
        except ObjectDoesNotExist:
            # We are happy that the password doesn't match any of the previous passwords.
            pass
        
        # CHECK-2: If it doesn't match the past N hashes, delete the oldest password hash if there are already N (current + (N-1)) previous) password hashes in the database.
        previousPasswordHashesForThisUser = PreviousPasswordHashes.objects.filter(referencedUser_id = self.referencedUser.id).order_by('dbEntryCreationDateTime')
        if len(previousPasswordHashesForThisUser) >= Users.PASSWORD_HISTORY_LENGTH:
            previousPasswordHashToBeDeleted = previousPasswordHashesForThisUser[0]
            previousPasswordHashToBeDeleted.delete()


    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name="Previous Password Hash"
        verbose_name_plural="Previous Password Hashes"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'referencedUser', 
                    'passwordHash',
                    ], 
                name='unique_User_PasswordHash_PreviousPasswordHashes_Relationship',
                )
            ]
    


