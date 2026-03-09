from InfrastructureApp.urls import  generateURLPatterns
from . import views

urlConfs = [
    {
        "viewRoute": "Login/".lower(),
        #"viewObject": LoginView.as_view(),
        "viewObject": views.ToolkitLoginView.as_view(),
        "urlConfIdentifier": "ToolkitAdminApp.ToolkitLoginView",
        "showInMenus": False,
        "childURLConfs": None,          # list of dict-type objects (i.e., a [{}] type object) for the sub-menus.
    },
    {
        "viewRoute": "LoginOTP/".lower(),
        "viewObject": views.ToolkitLoginOTPUsageView.as_view(),
        "urlConfIdentifier": "ToolkitAdminApp.ToolkitLoginOTPUsageView",
        "showInMenus": False,
        "childURLConfs": None,          # list of dict-type objects (i.e., a [{}] type object) for the sub-menus.
    },
    {
        "viewRoute": "PasswordReset/".lower(),
        "viewObject": views.ToolkitPasswordResetView.as_view(),
        "urlConfIdentifier": "ToolkitAdminApp.ToolkitPasswordResetView",
        "showInMenus": False,
        "childURLConfs": None,          # list of dict-type objects (i.e., a [{}] type object) for the sub-menus.
    },
    {
        "viewRoute": "PasswordResetOTPUsage/".lower(),
        "viewObject": views.PasswordResetOTPUsageView.as_view(),
        "urlConfIdentifier": "ToolkitAdminApp.PasswordResetOTPUsageView",
        "showInMenus": False,
        "childURLConfs": None,          # list of dict-type objects (i.e., a [{}] type object) for the sub-menus.
    },
    {
        "viewRoute": "logout/".lower(),
        "viewObject": views.ToolkitLogoutView.as_view(),
        "urlConfIdentifier": "ToolkitAdminApp.ToolkitLogoutView",
        "showInMenus": True,
        "childURLConfs": None,          # list of dict-type objects (i.e., a [{}] type object) for the sub-menus.
    },
]

urlpatterns = generateURLPatterns(urlConfs)