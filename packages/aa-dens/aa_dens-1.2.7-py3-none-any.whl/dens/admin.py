"""Admin site."""

from django.contrib import admin
from django.db.models import QuerySet

from dens.models import DenOwner, MercenaryDen, MercenaryDenReinforcedNotification


@admin.action(description="***Delete selected disabled owners, NO CONFIRMATION***")
def delete_inactive_owners(modeladmin, request, queryset: QuerySet[DenOwner]):
    queryset.filter(is_enabled=False).delete()


class DenOwnerUserFilter(admin.SimpleListFilter):
    """Filters the DenOwners by their user"""

    title = "user"
    parameter_name = "user"

    def lookups(self, request, model_admin):
        return DenOwner.objects.values_list(
            "character_ownership__user__id", "character_ownership__user__username"
        ).distinct()

    def queryset(self, request, queryset: QuerySet[DenOwner]):
        if value := self.value():
            return queryset.filter(character_ownership__user__id=value)
        else:
            return queryset


@admin.register(DenOwner)
class DenOwnerAdmin(admin.ModelAdmin):
    list_display = ["character_name", "user_name", "dens_count", "is_enabled"]
    readonly_fields = ["character_ownership"]
    list_filter = ["is_enabled", DenOwnerUserFilter]
    actions = [delete_inactive_owners]

    def has_add_permission(self, request):
        return False

    @admin.display(description="#Dens anchored under this owner")
    def dens_count(self, owner: DenOwner):
        return len(MercenaryDen.objects.get_owner_dens_ids_set(owner))


class DenUserFilter(admin.SimpleListFilter):
    """Filters the MercenaryDens by their user"""

    title = "user"
    parameter_name = "user"

    def lookups(self, request, model_admin):
        return MercenaryDen.objects.values_list(
            "owner__character_ownership__user__id",
            "owner__character_ownership__user__username",
        ).distinct()

    def queryset(self, request, queryset: QuerySet[DenOwner]):
        if value := self.value():
            return queryset.filter(owner__character_ownership__user__id=value)
        else:
            return queryset


@admin.register(MercenaryDen)
class MercenaryDenAdmin(admin.ModelAdmin):
    list_display = ["location", "owner", "is_reinforced", "reinforcement_time"]
    list_filter = ["owner", DenUserFilter]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=...):
        return False


@admin.register(MercenaryDenReinforcedNotification)
class MercenaryDenReinforcedNotificationAdmin(admin.ModelAdmin):
    list_display = ["den", "reinforced_by", "enter_reinforcement", "exit_reinforcement"]
    search_fields = [
        "reinforced_by__character_name",
        "reinforced_by__corporation_name",
        "reinforced_by__alliance_name",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        return False

    def has_change_permission(self, request, obj=...):
        return False
