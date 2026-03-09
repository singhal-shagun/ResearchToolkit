from nicegui import ui
from ..Infrastructure.Views import InfrastructureView
from ..Infrastructure.Theme import frame

class SettingsPage(InfrastructureView):    
    pageTitle = "Settings"

    def __call__(self, *args, **kwds):
        super().__call__(*args, **kwds)
        with frame():
            with ui.row():
                ui.label(text="SCOPUS API Key")