from django.db import models
from django.contrib.auth import get_user_model
from InfrastructureApp.db.models import InfrastructureModel
from django.core.exceptions import ObjectDoesNotExist
import secrets
import string
from django.utils import timezone
import datetime
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def tenMinutesDelayedDateTime():
    return (timezone.now() + datetime.timedelta(minutes = 10))

# Create your models here.
# [NOTE:] I had to name this file differently to allow django's migration framework to locate the tenMinutesDelayedDateTime function above. 
# Otherwise, when this file was named LoginOTPs.py, when I would run the migrate command, it would get confused between the following:
#    ToolkitAdminApp.models.LoginOTPsModel.py -> def tenMinutesDelayedDateTime ()
#    ToolkitAdminApp.models.__init__.py --> class LoginOTPsModel --> def tenMinutesDelayedDateTime(self)
class LoginOTPs(InfrastructureModel):
    # REFERENCE FIELD DEFINITIONS
    referencedUser = models.OneToOneField(get_user_model(),
                                               on_delete=models.RESTRICT,
                                               verbose_name="USER",
                                               related_name='loginOTPsReferencedUser',
                                               help_text=r"Select the user for the following password reset OTP.")
    

    # MODEL FIELD DEFINITIONS
    otp = models.CharField(r"ONE-TIME PASSWORD",
                           max_length=16,
                           null=False,
                           blank=False,
                           unique=True,
                           help_text=r"One-time password.",)

    validTillDateTime = models.DateTimeField(r"VALID TILL DATE-TIME",
                                             null=False,
                                             blank=False,
                                             default=tenMinutesDelayedDateTime,
                                             help_text=r"This is the date-time when this entry was created. It's supposed to be system-generated and non-modifiable by any user.")

    # MODEL METHOD DEFINITIONS SECTION
    def __str__(self):
        return self.referencedUser.username

    def clean (self):
        """
        Here, we check if a Login OTP already exists for the selected user.
            - If it does, that OTP is deleted before creating a new OTP.
        Otherwise, proceed to creating a new OTP.
        """
        super().clean()
        try:
            existingOTPRecord = LoginOTPs.objects.get(referencedUser_id = self.referencedUser.id)
            existingOTPRecord.delete()
        except ObjectDoesNotExist:
            pass
        # correctlyFormattedOTPTrueFalse = False
        newOTP = None
        # while not correctlyFormattedOTPTrueFalse:
        while True:
            acceptableCharacters = string.ascii_letters + string.digits + string.punctuation
            newOTP = "".join(secrets.choice(acceptableCharacters) for i in range(16))
            try:
                validate_password(newOTP, user=self.referencedUser)
            except ValidationError:
                continue
            try:
                # If a similar OTP already exists, create a new OTP.
                LoginOTPs.objects.get(otp = newOTP)
            except ObjectDoesNotExist:
                self.otp = newOTP
                break
            # hasAlphabet = False
            # hasDigits = False
            # hasPunctuation = False
            # for character in newOTP:
            #     if character in string.ascii_letters:
            #         hasAlphabet = True
            #     if character in string.digits:
            #         hasDigits = True
            #     if character in string.punctuation:
            #         hasPunctuation = True
            #     if (hasAlphabet and hasDigits and hasPunctuation):
            #         break
            # if (hasAlphabet and hasDigits and hasPunctuation):
            #     try:
            #         # If a similar OTP already exists, create a new OTP.
            #         LoginOTPs.objects.get(otp = newOTP)
            #     except ObjectDoesNotExist:
            #         self.otp = newOTP

            #         correctlyFormattedOTPTrueFalse = True



    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


    # MODEL CLASS META
    class Meta:
        ordering = ['referencedUser',]
        verbose_name="Login OTP"
        verbose_name_plural="Login OTPs"