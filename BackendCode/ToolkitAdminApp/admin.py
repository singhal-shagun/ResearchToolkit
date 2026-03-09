import copy
from django.contrib import admin
from InfrastructureApp.admin import InfrastructureModelAdmin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class InvalidLoginCounterAdmin(InfrastructureModelAdmin):
    autocomplete_fields = ['parentUser', ]
    fields = ['parentUser', 'invalidLoginCounter', ]
    list_display = copy.deepcopy(fields)
    search_fields = ['parentUser__username', ]
    search_help_text = """Seach using any user's username in the database."""


class LoginOTPsAdmin(InfrastructureModelAdmin):
    autocomplete_fields = ['referencedUser', ]
    fields = ['referencedUser', ]
    list_display = copy.deepcopy(fields) + ['otp', 'validTillDateTime', ]
    search_fields = ['referencedUser__username', 'referencedEquivalentUser__username',]
    search_help_text = """Seach using any user's username in the database."""


class PasswordResetOTPsAdmin(InfrastructureModelAdmin):
    autocomplete_fields = ['referencedUser', ]
    fields = ['referencedUser', ]
    list_display = copy.deepcopy(fields) + ['otp', 'validTillDateTime', ]
    search_fields = ['referencedUser__username', 'referencedEquivalentUser__username',]
    search_help_text = """Seach using any user's username in the database."""


class PreviousPasswordHashesAdmin(InfrastructureModelAdmin):
    autocomplete_fields = ['referencedUser', ]
    fields = ['referencedUser', 'passwordHash']
    readonly_fields = copy.deepcopy(fields)        # don't allow a user either to add new objest or to edit existing objects.
    list_display = copy.deepcopy(fields)
    search_fields = ['referencedUser__username', ]
    search_help_text = """Seach using any user's username in the database."""


class UserEquivalencesAdmin(InfrastructureModelAdmin):
#class UserEquivalencesAdmin(admin.ModelAdmin):
    autocomplete_fields = ['referencedOriginalUser', 'referencedEquivalentUser', ]
    fields = ['referencedOriginalUser', 'referencedEquivalentUser', ]
    list_display = copy.deepcopy(fields)
    search_fields = ['referencedOriginalUser__username', 'referencedEquivalentUser__username',]
    search_help_text = """Seach using any of the following fields in the database: 
        Original user's username; 
        Equivalent user's username."""
        
# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(InvalidLoginCounter, InvalidLoginCounterAdmin)
admin.site.register(LoginOTPs, LoginOTPsAdmin)
admin.site.register(PasswordResetOTPs, PasswordResetOTPsAdmin)
admin.site.register(PreviousPasswordHashes, PreviousPasswordHashesAdmin)
admin.site.register(UserEquivalences, UserEquivalencesAdmin)