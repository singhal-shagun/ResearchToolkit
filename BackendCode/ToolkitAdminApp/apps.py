from django.apps import AppConfig


class ToolkitAdminAppConfig(AppConfig):
    name = 'ToolkitAdminApp'
    verbose_name="Admin data sets"

    def ready(self) -> None:
        """
        [From Django's codebase](https://github.com/django/django/blob/b0788a0918d0e12bc8878581d99adc3a79799f94/django/apps/config.py#L271C8-L271C8):
        Override this method in subclasses to run code when Django starts.

        [From Django Docs](https://docs.djangoproject.com/en/4.2/ref/applications/#django.apps.AppConfig.ready):
        This method is called as soon as the registry is fully populated.
        Although you can’t import models at the module-level where AppConfig classes are defined, you can import them in ready(), using either an import statement or get_model().
        If you’re registering model signals, you can refer to the sender by its string label instead of using the model class itself.

        [NOTE:] The following imports work only when they are made inside this method. If you make at the top of this file, the imports won't work.
        """
        from django.contrib.auth.signals import user_logged_in, user_logged_out
        from .signals import createUserSessionRelationshipUponLogin, deleteUserSessionRelationshipUponLogin
        
        user_logged_in.connect(createUserSessionRelationshipUponLogin)
        user_logged_out.connect(deleteUserSessionRelationshipUponLogin)
