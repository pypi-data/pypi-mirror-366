"""Views."""

from django_datatables_view.base_datatable_view import BaseDatatableView

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from esi.decorators import token_required

from allianceauth.eveonline.evelinks import dotlan
from allianceauth.services.hooks import get_extension_logger
from app_utils.views import link_html

from dens import tasks
from dens.models import ESI_SCOPES, DenOwner, MercenaryDen

logger = get_extension_logger(__name__)


@login_required
@permission_required("dens.basic_access")
def index(request):
    """Render index view."""
    return redirect("dens:dens")


@login_required
@permission_required("dens.basic_access")
def dens(request):
    """Render dens databatable"""
    return render(request, "dens/dens.html")


@login_required
@permission_required("dens.basic_access")
@token_required(scopes=ESI_SCOPES)
def add_owner(request, token):
    """View to add an owner"""
    character_ownership = get_object_or_404(
        request.user.character_ownerships.select_related("character"),
        character__character_id=token.character_id,
    )

    owner, created = DenOwner.objects.get_or_create(
        character_ownership=character_ownership
    )

    if not created:
        owner.enable()
        messages.success(
            request,
            _(
                "Successfully enabled owner %(owner_name)s. Starting to fetch mercenary dens."
            )
            % {"owner_name": owner.character_name},
        )
    else:
        messages.success(
            request,
            _(
                "Successfully created owner %(owner_name)s. Starting to fetch mercenary dens."
            )
            % {"owner_name": owner.character_name},
        )

    tasks.update_owner_dens.delay(owner.id)

    return redirect("dens:index")


# pylint: disable = too-many-ancestors
class MercenaryDensListJson(
    PermissionRequiredMixin, LoginRequiredMixin, BaseDatatableView
):
    """
    Datatable view rendering users mercenary dens
    """

    model = MercenaryDen
    permission_required = "dens.basic_access"
    columns = [
        "id",
        "owner_character_name",
        "owner_main_character_name",
        "planet_name",
        "solar_system_link",
        "location_html",
        "is_reinforced",
        "reinforcement_time",
        "region_name",
        "constellation_name",
        "solar_system_name",
    ]
    order_columns = [
        "pk",
    ]

    # pylint: disable = too-many-return-statements, inconsistent-return-statements
    def render_column(self, row: MercenaryDen, column):
        if column == "id":
            return row.pk

        if column == "owner_character_name":
            return row.owner.character_name

        if column == "owner_main_character_name":
            return (
                row.owner.character_ownership.user.profile.main_character.character_name
            )

        if column == "is_reinforced":
            return "Yes" if row.is_reinforced else "No"

        if column == "reinforcement_time":
            if reinforcement_time := row.reinforcement_time:
                return reinforcement_time.isoformat()
            return

        if result := self._render_location(row, column):
            return result

    def get_initial_queryset(self):
        user = self.request.user
        if user.has_perm("dens.manager"):
            den_query = MercenaryDen.objects.all()
        elif user.has_perm("dens.alliance_view"):
            alliance = self.request.user.profile.main_character.alliance
            den_query = MercenaryDen.objects.filter_alliance_dens(alliance)
        elif user.has_perm("dens.corporation_view"):
            corporation = self.request.user.profile.main_character.corporation
            den_query = MercenaryDen.objects.filter_corporation_dens(corporation)
        else:
            den_query = MercenaryDen.objects.filter_user_dens(user)
        return den_query

    def filter_queryset(self, qs):
        qs = self._apply_search_filter(
            qs, 0, "owner__character_ownership__character__character_name"
        )
        qs = self._apply_search_filter(
            qs,
            1,
            "owner__character_ownership__user__profile__main_character__character_name",
        )
        qs = self._apply_search_filter(
            qs, 6, "location__eve_solar_system__eve_constellation__eve_region__name"
        )
        qs = self._apply_search_filter(
            qs, 7, "location__eve_solar_system__eve_constellation__name"
        )
        qs = self._apply_search_filter(qs, 8, "location__eve_solar_system__name")

        qs = self._apply_reinforce_filter(qs)

        if search := self.request.GET.get("search[value]", None):
            # TODO improve search
            qs = qs.filter(location__name__istartswith=search)

        return qs

    # pylint: disable = too-many-return-statements
    def _render_location(self, row: MercenaryDen, column):
        """Renders location for mercenary den dataview display"""
        planet = row.location
        solar_system = planet.eve_solar_system
        constellation = solar_system.eve_constellation
        region = constellation.eve_region

        if column == "planet_name":
            return planet.name

        if column == "solar_system_name":
            return solar_system.name

        if column == "region_name":
            return region.name

        if column == "constellation_name":
            return constellation.name

        if column == "solar_system_link":
            solar_system_link = format_html(
                '{}&nbsp;<span class="text-null-sec">{}</span>',
                link_html(
                    dotlan.solar_system_url(solar_system.name), solar_system.name
                ),
                round(solar_system.security_status, 1),
            )
            return solar_system_link

        if column == "location_html":
            location_html = format_html(
                "{}<br><em>{}</em>", constellation.name, region.name
            )
            return location_html

        return None

    def _apply_search_filter(self, qs, column_num, field) -> models.QuerySet:
        my_filter = self.request.GET.get(f"columns[{column_num}][search][value]", None)
        if my_filter:
            if self.request.GET.get(f"columns[{column_num}][search][regex]", False):
                kwargs = {f"{field}__iregex": my_filter}
            else:
                kwargs = {f"{field}__istartswith": my_filter}
            return qs.filter(**kwargs)
        return qs

    def _apply_reinforce_filter(self, qs):
        if filter_value := self.request.GET.get("columns[9][search][value]"):
            if "Yes" in filter_value:
                return qs.filter_is_reinforced(True)
            if "No" in filter_value:
                return qs.filter_is_reinforced(False)
            logger.warning("Unexpected input in reinforce filters: %s", filter_value)
        return qs


def dens_fdd_data(request) -> JsonResponse:
    """List for the drop-down fields"""
    qs = MercenaryDensListJson.get_initial_queryset(request)
    columns = request.GET.get("columns")
    result = {}
    if columns:
        for column in columns.split(","):
            options = _calc_options(request, qs, column)
            result[column] = sorted(list(set(options)), key=str.casefold)
    return JsonResponse(result, safe=False)


def _calc_options(request, qs, column):
    if column == "owner_character_name":
        return qs.values_list(
            "owner__character_ownership__character__character_name",
            flat=True,
        )

    if column == "owner_main_character_name":
        return qs.values_list(
            "owner__character_ownership__user__profile__main__character_name",
            flat=True,
        )

    return [f"** ERROR: Invalid column name '{column}' **"]
