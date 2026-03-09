from __future__ import annotations
from contextlib import contextmanager
from nicegui import ui
from .Constants import SiteConstants
from . import Menus
from typing import List
from .URLConfiguration import URLConfiguration

@contextmanager
def frame():
    """Defining the Page Layout elements here helps maintain consistency across all pages"""
    with ui.left_drawer(value=True, fixed=True, bordered=True, elevated=False, top_corner=False, bottom_corner=False) as left_drawer:
        populateMenu(menuURLConfigurations=Menus.leftDrawerMenu)


    with ui.header(value=True, fixed=False, bordered=True, elevated=True, wrap=True, add_scroll_padding=True):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu')
        ui.label(SiteConstants.SITE_TITLE)

    with ui.footer(value=True, fixed=False, bordered=True, elevated=True, wrap=True):
        ui.label(SiteConstants.COPYRIGHT_NOTICE)
        ui.space()
        ui.link(text=SiteConstants.CREDITS, target='https://icons8.com/icon/7W5fciOR3Cvk/brain', new_tab=True).style('color: white')
        ui.space()
        ui.label('Contact: info@example.com')
    
    yield


def populateMenu(menuURLConfigurations : List[URLConfiguration]):
    for item in menuURLConfigurations:
        if len(item.childURLConfigurations) == 0:
            try:
                # ui.menu_item(text=item.text, on_click=lambda item: ui.navigate.to(item.on_click), auto_close=True)
                ui.menu_item(text=item.text, on_click=lambda item: ui.navigate.to(item.on_click), auto_close=True)
                # ui.menu_item(text=item.text, on_click=item.on_click, auto_close=True)
            except KeyError as e:
                print(e)
        else:
            with ui.menu_item(text=item.text, on_click=lambda item: ui.navigate.to(item.on_click), auto_close=True):
                populateMenu(menuURLConfigurations=item.childURLConfigurations)

