from InfrastructureApp.constants import HTTPMethods
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from django.conf import settings


LOGIN_PRIVATE_KEY = "loginPrivateKey"
LOGIN_PUBLIC_KEY = "loginPublicKey"


def setEncryptionKeyPairInSession(request):
    if request.user.is_anonymous and (request.method.lower() == HTTPMethods.get):
        # Generate the public-private key-pair for RSA encryption-decyption of user password.
        # [NOTE:] we store the encryption keys in database as part of user session. 
        # They'll be deleted from session data in the database after decrypting the user password, if the user is authenticated successfully. 
        # (See post() for code where these keys are deleted.)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            )
        
        request.session[LOGIN_PRIVATE_KEY] = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            ).decode()
        
        public_key = private_key.public_key()
        request.session[LOGIN_PUBLIC_KEY] = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        

def decryptFields(privateKey: str, *valuesToBeDecrypted: list):
    private_key = serialization.load_pem_private_key(
        privateKey.encode(),    # converts the private key from str to bytes
        password=None,
    )
    decryptedValues = []
    for encryptedValue in valuesToBeDecrypted:
        try:
            encryptedValueInBase64Bytes = base64.b64decode(encryptedValue.encode('utf-8'))
            decryptedValueInBinaryFormat = private_key.decrypt(
                encryptedValueInBase64Bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decryptedValues.append(decryptedValueInBinaryFormat.decode())
        except ValueError as e:
            # Raised when there's a problem with decryption, say, when data wasn't encrypted at the client-end.
            # If the client didn't have an active internet connection, neither Pyodide, not python's Cryptography package would be loaded in its browser.
            # Hence, the client's data is passed unencrypted to the backend here.
            # Now, we'll check if we are in DEBUG mode (a proxy for development/debug environment).
            #   - If settings.DEBUG is True, we'll allow unencrypted values.
            #   - Else, when settings.DEBUG is False (i.e., in production environment), we will raise error. (Might show as "Server Error 500" to  production client)
            if settings.DEBUG:
                decryptedValues.append(encryptedValue)
            else:
                raise e
    return decryptedValues


def deleteEncryptionKeyPairFromSessionForAuthenticatedUsers(request):
    # If the user has been authenticated, delete the key-pair used to encrypt user credentials.
    if request.user.is_authenticated:
        if LOGIN_PRIVATE_KEY in request.session.keys():
            del request.session[LOGIN_PRIVATE_KEY]
        if LOGIN_PUBLIC_KEY in request.session.keys():
            del request.session[LOGIN_PUBLIC_KEY]