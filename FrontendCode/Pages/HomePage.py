from nicegui import ui
from ..Infrastructure.Views import InfrastructureView
from ..Infrastructure.Theme import frame

class HomePage(InfrastructureView):
    pageTitle = "Home"
    
    def __call__(self, *args, **kwds):
        super().__call__(*args, **kwds)
        with frame():
            ui.label(text="Welcome!")
