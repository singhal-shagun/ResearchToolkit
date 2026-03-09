from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class HTTPMethods:
    get : str = 'get'
    post : str = 'post'
    put : str = 'put'
    patch : str = 'patch'
    delete : str = 'delete'
    head : str = 'head'
    options : str = 'options'
    trace : str = 'trace'


class Users:
    # CLASS ATTRIBUTES DEFINITION.
    PASSWORD_HISTORY_LENGTH : int = 3

    class WebMaster:
        username = 'toolkit.webmaster'
        email = 'toolkit.webmaster@somedomain.com'

    class RootUser:
        username = 'toolkit.root'
        email = 'toolkit.root@somedomain.com'

    # METHOD DEFINITIONS.
    @classmethod
    def getSystemRootUserObject(cls):
        try:
            return get_user_model().objects.get(username = cls.RootUser.username)
        except:
            raise ValidationError("System root account not found.")
        

class PermissionsPrefixes:
    addPermissionPrefix = 'add_'
    changePermissionPrefix = 'change_'
    deletePermissionPrefix = 'delete_'
    readPermissionPrefix = 'view_'
