from pyscript import document
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64

def formValidation(fieldElements):

    for fieldElement in fieldElements:
        if (fieldElement.value.strip() == ""):
            fieldElement.value = ""

    formElement = document.querySelector('form')
    if not formElement.checkValidity():
        # Create the temporary button, click and remove it
        temporarySubmitButtonElement = document.createElement('button')
        formElement.appendChild(temporarySubmitButtonElement)
        temporarySubmitButtonElement.click()
        formElement.removeChild(temporarySubmitButtonElement)


def encrypt(public_key, fieldElements):


    if all([(fieldElement.value.strip() != "") for fieldElement in fieldElements]):
        for fieldElement in fieldElements:
            # 1. Get the plain-text value.
            plainTextValue = fieldElement.value

            # 2. Deserialize the public key into cyrptography library's public_key object
            public_key_object = serialization.load_pem_public_key(public_key.encode())

            # 3. Encrypt the plain-text value using the deserialized public key.
            encryptedValueInBytes = public_key_object.encrypt(
                plainTextValue.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # 4. Change the encrypted value's byte-encoding to base 64 so as to be able to serialize it into UTF-8 text.
            encryptedValueInUTF8Text = base64.b64encode(encryptedValueInBytes).decode('utf-8')
            
            # 5. Change the value to its encrypted form.
            fieldElement.value = encryptedValueInUTF8Text
    else:
         formValidation(fieldElements)