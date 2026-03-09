from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

class User (AbstractUser):
    previousPasswordHash = None


    # MODEL FIELD DEFINITIONS
    email = models.EmailField(_("email address"), 
                                null=False,
                                unique=True,
                                blank=False)

    # MODEL METHOD DEFINITIONS.
    def set_password(self, raw_password):
        """
        This is the overriden set_password() method. It does the following:
        1. Do self.previousPasswordHash = self.password. 
            The save() method of this class with pass self instance to password validators. 
            In PasswordNoveltyValidator, we'll save the previous and the newly created password hashes to the database.
        2. Call super().set_password(raw_password)
        """
        self.previousPasswordHash = self.password
        super().set_password(raw_password)



    # MODEL META DEFINITION.
    class Meta:
        db_table='auth_user'