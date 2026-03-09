from typing import Any, Dict
from InfrastructureApp.forms.forms import InfrastructureForm
from InfrastructureApp.forms.models import InfrastructureModelForm
from django.contrib.auth.forms import AuthenticationForm    #, PasswordResetForm
from django import forms
from django.contrib.auth import get_user_model
from ToolkitAdminApp.models import PasswordResetOTPs, LoginOTPs
from .models import InvalidLoginCounter
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from InfrastructureApp.constants import Users
from InfrastructureApp.EncryptionUtility import decryptFields, LOGIN_PRIVATE_KEY


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.error_messages["cryptographic_error"] = "Cryptography error. Please ensure access to public internet."
        self.error_messages[LOGIN_PRIVATE_KEY] = """Decryption key not found error. 
            Either using a cached copy of this page without a decryption key, or, your previous session has expired. 
            Please perform your operation again."""


    def clean(self) -> Dict[str, Any]:
        # 1. Get the Root User object.
        systemRootUserObject = Users.getSystemRootUserObject()
        
        # 2. Decrypt the user creditals and store them in the form's cleaned_Data dictionary for onward processing.
        # username = self.cleaned_data.get("username")
        # encryptedPasswordInUTF8Text = self.cleaned_data.get("password")
        # encryptedPasswordInBase64Bytes = base64.b64decode(encryptedPasswordInUTF8Text.encode('utf-8'))
        # private_key = serialization.load_pem_private_key(
        #     self.request.session[LOGIN_PRIVATE_KEY].encode(),
        #     password=None,
        # )
        # decryptedPasswordInPlainText = private_key.decrypt(
        #     encryptedPasswordInBase64Bytes,
        #     padding.OAEP(
        #         mgf=padding.MGF1(algorithm=hashes.SHA256()),
        #         algorithm=hashes.SHA256(),
        #         label=None
        #     )
        # )
        # password = self.cleaned_data["password"] = decryptedPasswordInPlainText.decode()

        valuesToBeDecrypted = [
            self.cleaned_data.get("username"),
            self.cleaned_data["password"]
        ]
        try:
            privateKey = self.request.session[LOGIN_PRIVATE_KEY]
        except KeyError:
            raise ValidationError(
                self.error_messages[LOGIN_PRIVATE_KEY],
                code=LOGIN_PRIVATE_KEY,
            )
        try:
            decryptedValues = decryptFields(privateKey, *valuesToBeDecrypted)
        except ValueError as e:
            raise ValidationError(
                self.error_messages["cryptographic_error"],
                code="cryptographic_error",
            )
        username = self.cleaned_data["username"] = decryptedValues[0]
        password = self.cleaned_data["password"] = decryptedValues[1]

        """
        SUMMARY:
        Here, we override the AuthenticationForm's clean() method to implement a lockout policy in case of 5 failed login attempts.
        Essentially, the AuthenticationForm's clean() method raises an exception for the following two cases:
            1. When the supplied credentials are incorrect.
            2. When the login attempt is being made against an inactive account.
        In either case, it seemed to return the 
        Hence, at the macro level, this method is designed using the try-catch mechanism:
            1. Check if the user exists. 
                1.1. If it does, get its corresponding InvalidLoginCounter object.
                1.2. If a corresponding InvalidLoginCounter object does not exist, create a one.
            2. Try user login.
                2.1. If it succeeds, reeset the InvalidLoginCounter object corresponding to this user.
                2.2. Return the cleaned data.
            3. Catch any exception raised by the super().clean() method.
                3.1. If the user exists, we undertake the rate limiting routine:
                    3.1.1. Increment the failed login counter.
                    3.1.2. If the counter reaches 5, lock the user account (by setting it as an inactive account).
                3.2. Raise an exception:
                    3.2.1. If the exception is on due to account lockout, raise that.
                    3.2.2. Otherwise, re-raise the exception as returned by the super().clean() method.
        """



        """
        Step-1: Check if the user exists.
                1.1. If it does, get its corresponding InvalidLoginCounter object.
                1.2. If a corresponding InvalidLoginCounter object does not exist, create a one.
        """
        # 1: Check if the user exists.
        try:
            userObject = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            userObject = None

        if userObject is not None:
            try:
                # 1.1. If the user exists, get its corresponding InvalidLoginCounter object.
                invalidLoginCounterObject = InvalidLoginCounter.objects.get(parentUser__username = username)
            except ObjectDoesNotExist:
                # 1.2. If a corresponding InvalidLoginCounter object does not exist, create a one.
                invalidLoginCounterObject = InvalidLoginCounter()
                invalidLoginCounterObject.parentUser_id = userObject.id
                invalidLoginCounterObject.createdBy = systemRootUserObject
                invalidLoginCounterObject.modifiedBy = systemRootUserObject

        try:
            """
            Step-2: Try user login
                2.1. If it succeeds, reeset the InvalidLoginCounter object corresponding to this user.
                2.2. Return the cleaned data.
            """
            # Try user login
            cleanedData = super().clean()

            # 2.1. User login successful. Reeset the InvalidLoginCounter object corresponding to this user.
            invalidLoginCounterObject.invalidLoginCounter = 0
            invalidLoginCounterObject.full_clean()
            invalidLoginCounterObject.save()

            # 2.2. Return the cleaned data.
            return cleanedData
        except Exception as e:
            """
            Step-3: Catch any exception raised by the super().clean() method.
                3.1. If the user exists, we undertake the rate limiting routine:
                    3.1.1. Increment the failed login counter.
                    3.1.2. If the counter reaches 5, lock the user account (by setting it as an inactive account).
                3.2. Raise an exception:
                    3.2.1. If the exception is on due to account lockout, raise that.
                    3.2.2. Otherwise, re-raise the exception as returned by the super().clean() method.
            """
            # 3.1. If the user exists, we undertake the rate limiting routine:
            if userObject is not None:
                # 3.1.1. Increment the failed login counter using SystemRoot account.
                if invalidLoginCounterObject.invalidLoginCounter < 5:
                    invalidLoginCounterObject.invalidLoginCounter += 1
                    invalidLoginCounterObject.createdBy = systemRootUserObject
                    invalidLoginCounterObject.modifiedBy = systemRootUserObject
                    invalidLoginCounterObject.full_clean()
                    invalidLoginCounterObject.save()
                
                # 3.1.2. If the counter reaches 5, lock the user account (by setting it as an inactive account).
                if (invalidLoginCounterObject.invalidLoginCounter >= 5) and userObject.is_active:
                    userObject.is_active = False
                    userObject.full_clean()
                    userObject.save()
            
                # 3.2. Raise an exception.
                # 3.2.1. If the exception is on due to account lockout, raise that.
                if not userObject.is_active:
                    raise ValidationError(
                        self.error_messages["inactive"],
                        code="inactive",
                    )
            # 3.2.2. Re-raise the exception returned by the super().clean() method.
            raise e


class LoginOTPUsageForm(LoginForm):
    # Defining username and password fields isn't required because they'll be inherited from superclass.
    # username = get_user_model()._meta.get_field("username").formfield()
    # password = get_user_model()._meta.get_field("username").formfield()

    # Using form field from LoginOTPs model stopped working since I had to implement encryption because encrypted length was too long.
    # Because the model imposed a limit on the length of 16 characters on the OTP, django refused to supply the encrypted text as part of the form's cleaned_data dictionary.
    # otp = LoginOTPs._meta.get_field("otp").formfield()    
    otp = forms.CharField()

    def clean(self) -> Dict[str, Any]:
        # 1. Decrypt  decrypt the username and password using super().clean().
        cleanedData = super().clean()

        # 2. Decrypt the OTP.
        valuesToBeDecrypted = [
            self.cleaned_data.get("otp"),
        ]
        try:
            privateKey = self.request.session[LOGIN_PRIVATE_KEY]
        except KeyError:
            raise ValidationError(
                self.error_messages[LOGIN_PRIVATE_KEY],
                code=LOGIN_PRIVATE_KEY,
            )
        try:
            decryptedValues = decryptFields(privateKey, *valuesToBeDecrypted)
        except ValueError as e:
            raise ValidationError(
                self.error_messages["cryptographic_error"],
                code="cryptographic_error",
            )
        self.cleaned_data["otp"] = decryptedValues[0]

        """
        For some reason, caling super().clean() and returning the cleaneddata dictionary doesn't work with DEBUG=False.
        It works with DEBUG=True; not with DEBUG=False in production environment.
        That's why, I've commented it even for DEBUG=False.
        """
        # cleanedData = super().clean()
        return self.cleaned_data
        

class PasswordResetForm(InfrastructureForm):
    # username = get_user_model()._meta.get_field("username").formfield()
    username = forms.CharField()

    error_messages = {
        "cryptographic_error" :"Cryptography error. Please ensure access to public internet.",
        LOGIN_PRIVATE_KEY : """Decryption key not found error. 
            Either using a cached copy of this page without a decryption key, or, your previous session has expired. 
            Please perform your operation again."""
    }
        
    def clean(self) -> Dict[str, Any]:
        cleanedData = super().clean()

        valuesToBeDecrypted = [
            self.cleaned_data.get("username"),
        ]
        try:
            privateKey = self.request.session[LOGIN_PRIVATE_KEY]
        except KeyError:
            raise ValidationError(
                self.error_messages[LOGIN_PRIVATE_KEY],
                code=LOGIN_PRIVATE_KEY,
            )
        try:
            decryptedValues = decryptFields(privateKey, *valuesToBeDecrypted)
        except ValueError as e:
            raise ValidationError(
                self.error_messages["cryptographic_error"],
                code="cryptographic_error",
            )
        self.cleaned_data["username"] = decryptedValues[0]

        """
        For some reason, caling super().clean() and returning the cleaneddata dictionary doesn't work with DEBUG=False.
        It works with DEBUG=True; not with DEBUG=False in production environment.
        That's why, I've commented it even for DEBUG=False.
        """
        # cleanedData = super().clean()
        return self.cleaned_data
        

class PasswordResetOTPUsageForm(InfrastructureForm):
    # username = get_user_model()._meta.get_field("username").formfield()
    # otp = PasswordResetOTPs._meta.get_field("otp").formfield()

    username = forms.CharField()
    otp = forms.CharField()

    error_messages = {
        "cryptographic_error" :"Cryptography error. Please ensure access to public internet.",
        LOGIN_PRIVATE_KEY : """Decryption key not found error. 
            Either using a cached copy of this page without a decryption key, or, your previous session has expired. 
            Please perform your operation again."""
    }

    def clean(self) -> Dict[str, Any]:
        cleanedData = super().clean()
        
        valuesToBeDecrypted = [
            self.cleaned_data.get("username"),
            self.cleaned_data["otp"]
        ]
        try:
            privateKey = self.request.session[LOGIN_PRIVATE_KEY]
        except KeyError:
            raise ValidationError(
                self.error_messages[LOGIN_PRIVATE_KEY],
                code=LOGIN_PRIVATE_KEY,
            )
        try:
            decryptedValues = decryptFields(privateKey, *valuesToBeDecrypted)
        except ValueError as e:
            raise ValidationError(
                self.error_messages["cryptographic_error"],
                code="cryptographic_error",
            )
        self.cleaned_data["username"] = decryptedValues[0]
        self.cleaned_data["otp"] = decryptedValues[1]

        """
        For some reason, caling super().clean() and returning the cleaneddata dictionary doesn't work with DEBUG=False.
        It works with DEBUG=True; not with DEBUG=False in production environment.
        That's why, I've commented it even for DEBUG=False.
        """
        # cleanedData = super().clean()
        return self.cleaned_data