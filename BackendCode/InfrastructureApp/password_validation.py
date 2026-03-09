from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext as _
import string
from InfrastructureApp.constants import Users
from ToolkitAdminApp.models import PreviousPasswordHashes
from django.contrib.auth.hashers import make_password, check_password
from InfrastructureApp.constants import Users


class MaximumLengthValidator:
    """
    Validates that the password is not too long.
    """
    def __init__(self, max_length=20):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password must contain at max %(max_length)d characters."),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at max %(max_length)d characters."
            % {"max_length": self.max_length}
        )
    

class UpperCaseALphabetValidator:
    """
    Validates that the password contains at least 1 UpperCase alphabet.
    """
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 uppercase alphabet (A-Z)."),
                code="uppercase_alphabet_not_found",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase alphabet (A-Z)."
        )
    

class LowerCaseALphabetValidator:
    """
    Validates that the password contains at least 1 LowerCase alphabet.
    """
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 lowercase alphabet (A-Z)."),
                code="uppercase_alphabet_not_found",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase alphabet (A-Z)."
        )
    

class NumbersValidator:
    """
    Validates that the password contains at least 1 number (0-9).
    """
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 number (0-9)."),
                code="alphabet_not_found",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 number (0-9)."
        )
    

class SymbolValidator:
    """
    Validates that the password contains at least 1 symbol (special character).
    """
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(char in string.punctuation for char in password):
            raise ValidationError(
                _("This password must contain at least 1 special character (%{symbols})."),
                code="uppercase_alphabet_not_found",
                params={"symbols": string.punctuation},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol %(symbols)s characters."
            % {"symbols": string.punctuation}
        )


class PasswordNoveltyValidator:
    """
    Validates that the password is not same as the last 'N' passwords.
    Default N-value is as per the Users.PASSWORD_HISTORY_LENGTH constant.
    """
    def __init__(self, N=Users.PASSWORD_HISTORY_LENGTH):
        self.N = N

    def validate(self, password, user=None):
        if user is None:
            # we need to know the user to validate if the password is the same as any of the last N passwords.
            raise ValidationError("Unknown user.")

        # Since the user is known, we can continue validating if the password is the same as any of the last N passwords.
        # hashedNewPassword = make_password(password)
        # try:
        #     PreviousPasswordHashes.objects.get(referencedUser_id = user.id, passwordHash = hashedNewPassword)
        #     # No exception raised, implying the password isn't novel.
        #     novelPasswordBoolean = False
        # except ObjectDoesNotExist:
        #     novelPasswordBoolean = True
        
        # if not novelPasswordBoolean:
        #     raise ValidationError(
        #         _(PreviousPasswordHashes.errorMessage),
        #         code="password_not_novel",
        #         params={},
        #     )
        previousPasswordHashes = PreviousPasswordHashes.objects.filter(referencedUser_id = user.id)
        for previousPasswordHash in previousPasswordHashes:
            if check_password(password, previousPasswordHash.passwordHash):
                # Password re-use detected.
                raise ValidationError(
                    _(PreviousPasswordHashes.errorMessage),
                    code="password_not_novel",
                    params={},
                )


    def get_help_text(self):
        return PreviousPasswordHashes.errorMessage


    def password_changed(self, raw_password, user):
        """
        METHOD PARAMETERS:
        - raw_password: the newly set password (in raw unhashed form)
        - user: the user instance

        This method's workflow is as follows:
        1. Ensure that a user instance is provided, else, raise an exception.
        2. Save the previous password's hash to the PreviousPasswordHashes model, if it's not already present.
        3. Save the new password's hash to the PreviousPasswordHashes model, if it's not already present.
        """
        systemRootUser = Users.getSystemRootUserObject()

        # 1. Ensure that a user instance is provided, else, raise an exception.
        if user is None:
            raise Exception("Password updated, but previous password hash couldn't be saved because user instance not was provided.")
        
        # 2. Save the previous password's hash to the PreviousPasswordHashes model, if it's not already present.
        if user.previousPasswordHash != "": # when a new user account is created, it has no previous password hash and hence, no need to save it.
            try:
                PreviousPasswordHashes.objects.get(referencedUser_id = user.id, passwordHash = user.previousPasswordHash)
            except ObjectDoesNotExist:
                previousPasswordHash = PreviousPasswordHashes()
                previousPasswordHash.referencedUser = user
                previousPasswordHash.passwordHash = user.previousPasswordHash
                previousPasswordHash.modifiedBy = systemRootUser
                previousPasswordHash.createdBy = systemRootUser
                previousPasswordHash.full_clean()
                previousPasswordHash.save()
            
        
        # 3. Save the new password's hash to the PreviousPasswordHashes model, if it's not already present.
        try:
            PreviousPasswordHashes.objects.get(referencedUser_id = user.id, passwordHash = user.password)
        except ObjectDoesNotExist:
            previousPasswordHash = PreviousPasswordHashes()
            previousPasswordHash.referencedUser = user
            previousPasswordHash.passwordHash = user.password
            previousPasswordHash.modifiedBy = systemRootUser
            previousPasswordHash.createdBy = systemRootUser
            previousPasswordHash.full_clean()
            previousPasswordHash.save()
