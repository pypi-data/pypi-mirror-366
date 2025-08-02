from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_adverse_event.constants import STUDY_TERMINATION_CONCLUSION_ACTION
from edc_adverse_event.model_mixins import (
    AeFollowupModelMixin,
    AeInitialModelMixin,
    AesiModelMixin,
    AeSusarModelMixin,
    AeTmgModelMixin,
    DeathReportModelMixin,
    DeathReportTmgModelMixin,
    DeathReportTmgSecondModelMixin,
    HospitalizationModelMixin,
)
from edc_consent.field_mixins.identity_fields_mixin import IdentityFieldsMixin
from edc_consent.field_mixins.personal_fields_mixin import PersonalFieldsMixin
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_consent.model_mixins import ConsentModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OnScheduleModelMixin
from edc_visit_schedule.model_mixins.off_schedule_model_mixin import (
    OffScheduleModelMixin,
)
from edc_visit_tracking.model_mixins import VisitModelMixin


class SubjectConsent(
    SiteModelMixin,
    ConsentModelMixin,
    PersonalFieldsMixin,
    IdentityFieldsMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    class Meta(ConsentModelMixin.Meta):
        pass


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()
    on_site = CurrentSiteByCdefManager()

    class Meta:
        proxy = True


class SubjectVisit(SiteModelMixin, VisitModelMixin, BaseUuidModel):
    appointment = models.OneToOneField(
        "edc_appointment.appointment", on_delete=PROTECT, related_name="ae_appointment"
    )


class CrfOne(SiteModelMixin, NonUniqueSubjectIdentifierModelMixin, BaseUuidModel):
    report_datetime = models.DateTimeField(default=get_utcnow)


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    """A model used by the system. Auto-completed by subject_consent."""

    class Meta(OnScheduleModelMixin.Meta):
        pass


class StudyTerminationConclusion(
    SiteModelMixin, ActionModelMixin, OffScheduleModelMixin, BaseUuidModel
):
    action_name = STUDY_TERMINATION_CONCLUSION_ACTION

    subject_identifier = models.CharField(max_length=50, unique=True)

    class Meta(OffScheduleModelMixin.Meta):
        pass


class AeInitial(AeInitialModelMixin, BaseUuidModel):
    class Meta(AeInitialModelMixin.Meta):
        pass


class AeFollowup(AeFollowupModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeFollowupModelMixin.Meta):
        pass


class Aesi(AesiModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AesiModelMixin.Meta):
        pass


class AeSusar(AeSusarModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeSusarModelMixin.Meta):
        pass


class AeTmg(AeTmgModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeTmgModelMixin.Meta):
        pass


class DeathReport(DeathReportModelMixin, BaseUuidModel):
    class Meta(DeathReportModelMixin.Meta):
        pass


class DeathReportTmg(DeathReportTmgModelMixin, BaseUuidModel):
    class Meta(DeathReportTmgModelMixin.Meta):
        pass


class DeathReportTmgSecond(DeathReportTmgSecondModelMixin, DeathReportTmg):
    class Meta(DeathReportTmgSecondModelMixin.Meta):
        proxy = True


class Hospitalization(
    HospitalizationModelMixin, ActionModelMixin, SiteModelMixin, BaseUuidModel
):
    class Meta(HospitalizationModelMixin.Meta):
        pass
