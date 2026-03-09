from nicegui import APIRouter
from ..Infrastructure.Constants.Site import SiteConstants

class InfrastructureAPIRouter(APIRouter):
    def page(self, path, *, title = None, viewport = None, favicon = None, dark = ..., response_timeout = 3, **kwargs):
        redefinedTitle = title + " - " + SiteConstants.SITE_TITLE
        return super().page(path, title=redefinedTitle, viewport=viewport, favicon=favicon, dark=dark, response_timeout=response_timeout, **kwargs)
    