from importlib import import_module
from django.urls import path, include
from ToolkitAdminApp import UNAUTHORIZED_USER
from django.contrib.auth.views import LoginView, PasswordResetView
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin

#def includeURLResolversFromOtherApps(urlConfs):
#    """
#    This function is use to include other apps' URLConfs in an app.
#    You should ned to call this function outside of the your root project's urls.py.

#    INPUT PARAMETERS:
#    """
#    urlpatterns = []
#    for urlConf in urlConfs:
#        if isinstance(urlConf["urlConfModule"], str):   # when you've provided a string name of the package containing the urlpatterns.
#            urlpatterns.append(
#                path(urlConf["appRoute"], include(urlConf["urlConfModule"]), name = urlConf["urlConfIdentifier"])
#                )
#        else:                                           # when you've provided the urlpatterns as a list/tuple.
#            urlpatterns.append(
#                path(urlConf["appRoute"], urlConf["urlConfModule"], name = urlConf["urlConfIdentifier"])
#                )
#    return urlpatterns


def createRoute(parentRoute, childRoute):
    createdRoute = None
    if parentRoute.endswith("/"):
        createdRoute = parentRoute + childRoute
    else:
        createdRoute = "/".join([parentRoute, childRoute])

    if  (createdRoute[0] != "/"):
        createdRoute = "/" + createdRoute
    return createdRoute


def generateURLPatterns(urlConfs):
    urlpatterns = []
    for urlConf in urlConfs:
        route = urlConf["viewRoute"]
        #route = createRoute(parentRoute, urlConf["viewRoute"])
        viewObject = urlConf["viewObject"]
        urlConfIdentifier = urlConf["urlConfIdentifier"]
        childURLConfs = urlConf["childURLConfs"]

        """
        This code section generates the urlpatterns from the urlConf.
        """
        if (viewObject is not None):
            urlpatterns.append(
                path(route, viewObject, name = urlConfIdentifier)
                )
        
        if (childURLConfs != None):                        # Case when you're going to get child URLConfs.
            if ((not route.endswith("/")) and (route != "")):
                route += "/"
            if isinstance(childURLConfs, str):   # when you've provided a string name of the package containing the urlpatterns.
                urlpatterns.append(
                    path(route, include(childURLConfs), name = urlConfIdentifier)
                    )
            elif isinstance(childURLConfs, (list, tuple)):                # when you've provided the urlpatterns as a list/tuple.
                firstURLConf = childURLConfs[0]
                if (type(firstURLConf) is not dict):
                    urlpatterns.append(
                        path(route, childURLConfs, name = urlConfIdentifier)
                        )
                else:   # when the child urlConf elements are dict-type, those are our Toolkit's URL entries and we need to call this function recursively.
                    childURLPatterns = generateURLPatterns(childURLConfs)
                    urlpatterns.append(
                        path(route, include(childURLPatterns), name = urlConfIdentifier)
                        )

    return urlpatterns



def populateMenu(context, parentRoute, urlConfs):

    menu = []

    for urlConf in urlConfs:

        if (urlConf["urlConfIdentifier"] == "AdministrationSide"):
            # We don't want to put up a link to Admin on the front-end.
            continue

        
        route = urlConf["viewRoute"]
        viewObject = urlConf["viewObject"]
        urlConfIdentifier = urlConf["urlConfIdentifier"]
        childURLConfs = urlConf["childURLConfs"]
        menuItem = {}

        """
        Ensures that for a menu-item to be created, the view has to be a Class-based View (CBV).
        Menu-items will not be created for Function-based Views (FBV).
        """
        if hasattr(viewObject, "view_class"):
            if ("displayText" in urlConf.keys()):
                raise Exception("URLConfs corresponding to Class-based Views cannot have the 'displayText' key.")
            elif issubclass(viewObject.view_class, (LoginView, PasswordResetView)):
                # No need to include LoginView and PasswordResetView in the Menu.
                continue
            else:
                if issubclass(viewObject.view_class, LoginRequiredMixin):
                    if not context.request.user.is_authenticated:
                        continue    # For unauthenticated users, do not add such URLConfs to the Menu that require user login & authentication.

                permissionsCheckTrueFalse = False
                # if hasattr(viewObject.view_class, "candidate_permission_required"):
                if hasattr(viewObject, "candidate_permission_required"):
                    # Certain views will have "candidate_permission_required", indicating that the user needs to have ATLEAST ONE of those permissions.
                    if (len(viewObject.candidate_permission_required) > 0):
                        permissions_required = UNAUTHORIZED_USER
                        for permission in viewObject.candidate_permission_required:
                            permissionsCheckTrueFalse = context.request.user.has_perm(permission)
                            if permissionsCheckTrueFalse:
                                permissions_required = permission
                                break
                    else:
                        permissions_required = "No permissions required; only Login required."
                        permissionsCheckTrueFalse = True
                else:
                    # Otherwise, the user needs to have ALL the permissions specified in the view object's permission_required attribute.
                    permissions_required = viewObject.view_class.permission_required
                    permissionsCheckTrueFalse = context.request.user.has_perms(permissions_required)

                if (permissions_required != UNAUTHORIZED_USER):
                    if (permissionsCheckTrueFalse and urlConf["showInMenus"]):
                        # 1. Assign the menu-item's title.
                        menuItem["displayText"] = viewObject.view_class.title
                        # 2. assign menu-item's route
                        menuItem["viewRoute"] = createRoute(parentRoute, route)

        # 3. assign menu-item's child menu
        if (childURLConfs is None):
            if (not (menuItem == {})):
                menuItem["childMenu"] = None
                menu.append(menuItem)
        else:
            if isinstance(childURLConfs, str):   # when you've provided a string name of the package containing the urlConfs.
                childURLConfs = import_module(childURLConfs).urlConfs

            if (menuItem == {}):
                newParentRoute = createRoute(parentRoute, route)
                elevatedChildMenu = populateMenu(context, newParentRoute, childURLConfs)  # this function calls itself recursively with parentRoute
                if elevatedChildMenu is not None:
                    menu.append(elevatedChildMenu)
            else:
                menuItem["childMenu"] = populateMenu(context, menuItem["viewRoute"], childURLConfs)  # this function calls itself recursively with menuItem["viewRoute"]
                menu.append(menuItem)

    if (len(menu)>0):
        return menu
    else:
        return None


def getMenuHTML(context, parentMenu, menu):
    if parentMenu is None:
        menuHTML = ""
        childMenuHTML = None
        for menuItem in menu:
            try:
                viewRoute = menuItem['viewRoute']
                displayText = menuItem['displayText']
                childMenu = menuItem['childMenu']
            except Exception as e:
                raise e

            listItemClass = 'nav-item'
            anchorClass = 'nav-link'
            anchorOtherAttributes = 'href="' + viewRoute + '"'
                
            if childMenu is not None:
                childMenuHTML = getMenuHTML(context, viewRoute, childMenu)
                listItemClass += " dropdown"
                anchorClass += ' dropdown-toggle'
                anchorOtherAttributes += ' data-bs-toggle="dropdown" role="button" aria-expanded="false"'
                #anchorOtherAttributes += ' data-bs-toggle="popover" data-bs-trigger="hover focus" role="button" aria-expanded="false"'


            if (context.request.path == viewRoute):
                anchorClass += ' active'
                anchorOtherAttributes += ' aria-current="page" '

            listItemClass = '"' + listItemClass + '"'
            anchorClass = '"' + anchorClass + '"'
            menuItemHTML = ' '.join([
                '<li class=', listItemClass, '>', '<a class=', anchorClass, anchorOtherAttributes, '>', displayText, '</a>'
                ])


            if childMenuHTML is not None:
                menuItemHTML += childMenuHTML
            menuItemHTML += '</li>'
            menuHTML += menuItemHTML
    else:
        menuHTML = '<ul class="dropdown-menu">'
        childMenuHTML = None
        for menuItem in menu:
            viewRoute = menuItem['viewRoute']
            displayText = menuItem['displayText']
            childMenu = menuItem['childMenu']

            #listItemClass = 'nav-item'
            anchorClass = 'dropdown-item'
            anchorOtherAttributes = 'href="' + viewRoute + '"'

            if childMenu is not None:
                childMenuHTML = getMenuHTML(context, viewRoute, childMenu)
                #listItemClass += " dropdown"
                anchorClass += ' dropdown-toggle'
                anchorOtherAttributes += ' data-bs-toggle="dropdown" role="button" aria-expanded="false"'
                #anchorOtherAttributes += ' data-bs-toggle="popover" data-bs-trigger="hover focus" role="button" aria-expanded="false"'

            if (context.request.path == viewRoute):
                anchorClass += ' active'
                anchorOtherAttributes += ' aria-current="page" '

            anchorClass = '"' + anchorClass + '"'
            menuItemHTML = ' '.join([
                '<li><a class=', anchorClass, anchorOtherAttributes, '>', displayText, '</a></li>'
                ])

            if childMenuHTML is not None:
                menuItemHTML += childMenuHTML
            menuHTML += menuItemHTML
        menuHTML += '</ul>'
    return menuHTML
