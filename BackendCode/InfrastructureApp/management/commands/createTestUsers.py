from django.core import management
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from InfrastructureApp.constants import Users


UserModel = get_user_model()



class Command(management.base.BaseCommand):
    help = "Create test users: the root user and the users for every group in the database."

    def add_arguments(self, parser):
        # Although I've added loc, it's not supposed to do much because Django Docs didn't have call to super()... they had some custom implementation.
        # See https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
        super().add_arguments(parser)   

    def handle(self, *args, **options):
        #1. Create a systemroot superuser account.
        systemRootUsername = Users.RootUser.username
        adminUser = UserModel()
        adminUser.username = systemRootUsername
        adminUser.set_password('Authority@123#')
        adminUser.email = Users.RootUser.email
        adminUser.is_staff = True    
        adminUser.last_login = timezone.now()
        adminUser.is_superuser = True
        adminUser.save()


        #2. Create role-based staff-users.
        groups = Group.objects.all()
        for group in groups:
            testUser = UserModel()
            testUser.username = group.name.upper() + "_USER"
            testUser.set_password('Authority@123#')
            testUser.email = testUser.username + '@somedomain.com'    # Dummy email. Warn the Testers that they won't be able to login unless these emails are changed to actual emails by the ROOT user created above.
            testUser.is_staff = True
            testUser.last_login = timezone.now()
            testUser.save()
            testUser.groups.add(group)
