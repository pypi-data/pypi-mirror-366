"""Hooks for charlink application"""

from charlink.app_imports.utils import (  # pylint: disable=import-error
    AppImport,
    LoginImport,
)

from django.contrib import messages
from django.contrib.auth.models import Permission, User
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from allianceauth.eveonline.models import EveCharacter
from app_utils.django import users_with_permission

from dens import tasks
from dens.models import ESI_SCOPES, DenOwner


# pylint: disable=duplicate-code
def _add_character(request, token):
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


def _check_permissions(user: User) -> bool:
    return user.has_perm("dens.basic_access")


def _is_character_added(character: EveCharacter) -> bool:
    return DenOwner.objects.filter(character_ownership__character=character).exists()


def _users_with_perms():
    return users_with_permission(
        Permission.objects.get(content_type__app_label="dens", codename="basic_access")
    )


app_import = AppImport(
    "dens",
    [
        LoginImport(
            app_label="dens",
            unique_id="default",
            field_label=_("Mercenary Dens"),
            add_character=_add_character,
            scopes=ESI_SCOPES,
            check_permissions=_check_permissions,
            is_character_added=_is_character_added,
            is_character_added_annotation=Exists(
                DenOwner.objects.filter(
                    character_ownership__character_id=OuterRef("pk")
                )
            ),
            get_users_with_perms=_users_with_perms,
        )
    ],
)
