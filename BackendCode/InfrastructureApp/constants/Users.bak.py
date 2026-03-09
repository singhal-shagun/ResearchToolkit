from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# CONSTANTS AND MASTERDATA DEFINITIONS.
# PASSWORD_HISTORY_LENGTH = 3
# username = "username"
# email = "email"

# # SYSTEM USER ACCOUNT DEFINITIONS
# # WebMaster = {
# #     username: 'adss.webmaster',
# #     email: 'adss.webmaster@aai.aero'
# # }

# # RootUser = {
# #     username: 'adss.root',
# #     email: 'adss.root@aai.aero'
# # }


# # METHOD DEFINITIONS.
# def getSystemRootUserObject():
#     try:
#         return get_user_model().objects.get(username = RootUser[username])
#     except:
#         raise ValidationError("System root account not found.")