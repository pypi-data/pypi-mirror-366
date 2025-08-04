from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class DensMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Dens"),
            "fas fa-tents fa-fw",
            "dens:index",
            navactive=["dens:"],
        )

    def render(self, request):
        if request.user.has_perm("dens.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return DensMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "dens", r"^dens/")


@hooks.register("charlink")
def register_charlink_hook():
    return "dens.thirdparty.charlink_hook"
