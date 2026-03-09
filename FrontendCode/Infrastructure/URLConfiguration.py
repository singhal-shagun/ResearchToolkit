from __future__ import annotations
from typing import Optional, List
from nicegui import ui

class URLConfiguration:

    childURLConfigurations : List[URLConfiguration] = []

    def __init__(self, 
                 text : str, 
                 on_click : ui.page,
                 parentURLConfiguration : URLConfiguration | None, 
                 slotIndex : Optional[int] = None
                 ):
        """URL Configuration

        Initialize a URLConfiguration object for menu navigation.

        This class represents a configurable URL/menu item with a callback handler,
        supporting hierarchical menu structures through parent-child relationships.


        :param text: label of the menu item
        :param on_click: ui.page callable to be executed when this menu item is selected
        :param parentURLConfiguration: parent menu item to establish hierarchy (None for top-level items)
        :param slotIndex: reserved for future use to sort menu items in ascending order
        """
        self.text  = text
        self.on_click = on_click
        if parentURLConfiguration is not None:
            parentURLConfiguration.childURLConfigurations.append(self)