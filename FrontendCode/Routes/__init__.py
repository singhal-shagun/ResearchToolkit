from nicegui import ui, Client
from ..Infrastructure.APIRouter import InfrastructureAPIRouter
from ..Infrastructure import Menus
from ..Infrastructure.URLConfiguration import URLConfiguration
# from ..Pages.HomePage import HomePage
from ..Pages import HomePage, SettingsPage

router = InfrastructureAPIRouter(prefix='')

@router.page(path="/", title=HomePage.pageTitle)
def homePageView(): return HomePage()()
# homePageURLConfiguration = URLConfiguration(text=HomePage.pageTitle, on_click= lambda : ui.navigate.to(homePageView), parentURLConfiguration=None)
homePageURLConfiguration = URLConfiguration(text=HomePage.pageTitle, on_click= homePageView, parentURLConfiguration=None)
# homePageURLConfiguration = URLConfiguration(text=HomePage.pageTitle, on_click= Client.page_routes[homePageView], parentURLConfiguration=None)
Menus.leftDrawerMenu.append(homePageURLConfiguration)

@router.page(path="/settings", title=SettingsPage.pageTitle)
def settingsPageView(): return SettingsPage()()
Menus.leftDrawerMenu.append(URLConfiguration(text=SettingsPage.pageTitle, on_click= settingsPageView, parentURLConfiguration=None))
