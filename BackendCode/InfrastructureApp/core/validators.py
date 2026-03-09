#from decimal import Decimal
#from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils.deconstruct import deconstructible
from pathlib import Path
from django.core.exceptions import ValidationError
import magic
from InfrastructureApp.constants.FileAndMimeTypes import MimeTypes

# -- SECTION-1: OUT-OF-BOX VALIDATOR OBJECTS GO HERE. -- #
class ValidatorObjects:
    """
    This class contains all the out-of-box validators readily available for re-use in the project.
    """
    upperCaseAlphabetValidator = RegexValidator(r'^[A-Z]*$', 'Only UPPER CASE alphabets are allowed.')
    upperCaseAlphabetAndDigitsValidator = RegexValidator(r'^[A-Z0-9]*$', 'Only UPPER CASE alphabets [A-Z] and digits [0-9] are allowed.')


# -- SECTION-2: CUSTOMIZABLE VALIDATOR CLASSES GO HERE. WOULD NEED TO CREATE OBJECTS WHEN BEING USED IN MODELS/FORMS. -- #
@deconstructible
class FileExtensionAndHeaderValidator (FileExtensionValidator):
    """
    This code is inspired from Django's built-in FileExtensionValidator class. See:
    https://github.com/django/django/blob/2128a73713735fb794ca6565fd5d7792293f5cfa/django/core/validators.py#L561
    """
    code = "invalid_extension_or_mimetype"

    def __call__(self, value):
        """
        Since this validator is bound to be associated with Model's FileField objects, the 'value' parameter is bound to be a FieldFile object.
        """
        extension = Path(value.name).suffix[1:].lower() # value.name is equivalent to FieldFile's name attribute.

        # 1. Check if the extension is allowed.
        fileExtensionCheckBoolean = (self.allowed_extensions is not None) and (extension in self.allowed_extensions)

        # 2. Check if file's mime type is in conformity with the file extension.
        mimeType = magic.from_buffer(value.open('rb').read(), mime=True)
        try:
            fileMimeTypeCheckBoolean = (mimeType.lower() == MimeTypes[extension])
        except KeyError:    # This file's extension doesn't have an entry in MimeTypes
            fileMimeTypeCheckBoolean = False
        
        # 3. If either of the checks fail, raise a ValidationError.
        if not (fileExtensionCheckBoolean and fileMimeTypeCheckBoolean):
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "extension": extension,
                    "allowed_extensions": ", ".join(self.allowed_extensions),
                    "value": value,
                },
            )
