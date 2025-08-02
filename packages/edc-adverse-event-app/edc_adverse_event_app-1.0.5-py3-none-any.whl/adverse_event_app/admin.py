from django.contrib import admin
from edc_adverse_event.modeladmin_mixins import (
    AeFollowupModelAdminMixin,
    AeInitialModelAdminMixin,
    HospitalizationModelAdminMixin,
)
from edc_model_admin.history import SimpleHistoryAdmin

from .models import AeFollowup, AeInitial, Hospitalization


@admin.register(AeInitial)
class AeInitialAdmin(AeInitialModelAdminMixin, SimpleHistoryAdmin):
    pass


@admin.register(AeFollowup)
class AeFollowupAdmin(AeFollowupModelAdminMixin, SimpleHistoryAdmin):
    pass


@admin.register(Hospitalization)
class HospitalizationAdmin(HospitalizationModelAdminMixin, SimpleHistoryAdmin):
    pass
