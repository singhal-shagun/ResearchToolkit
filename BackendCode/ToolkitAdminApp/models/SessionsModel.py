from django.contrib.sessions.base_session import AbstractBaseSession, BaseSessionManager
# from django.contrib.sessions.models import SessionManager
from importlib import import_module
from django.conf import settings

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class SessionManager(BaseSessionManager):
    use_in_migrations = True



class Sessions(AbstractBaseSession):
    objects = SessionManager()

    @classmethod
    def get_session_store_class(cls):
        return SessionStore
    
    class Meta(AbstractBaseSession.Meta):
        db_table = "django_session"