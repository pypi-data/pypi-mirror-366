from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_constants.constants import GRADE4, MALE, NO, NOT_APPLICABLE, YES
from edc_utils import get_utcnow
from faker import Faker
from model_bakery.recipe import Recipe, seq

from .models import (
    AeFollowup,
    AeInitial,
    AeSusar,
    AeTmg,
    DeathReport,
    DeathReportTmg,
    DeathReportTmgSecond,
    SubjectConsent,
    SubjectConsentV1,
)

fake = Faker()

subjectconsent = Recipe(
    SubjectConsent,
    consent_datetime=get_utcnow() - relativedelta(months=1),
    dob=get_utcnow() + relativedelta(days=5) - relativedelta(years=25),
    first_name=fake.first_name,
    last_name=fake.last_name,
    initials="AA",
    gender=MALE,
    identity=seq("12315678"),
    confirm_identity=seq("12315678"),
    identity_type="passport",
    is_dob_estimated="-",
    screening_identifier=uuid4(),
    site=Site.objects.get_current(),
)


subjectconsentv1 = Recipe(
    SubjectConsentV1,
    consent_datetime=get_utcnow() - relativedelta(months=1),
    dob=get_utcnow() + relativedelta(days=5) - relativedelta(years=25),
    first_name=fake.first_name,
    last_name=fake.last_name,
    initials="AA",
    gender=MALE,
    identity=seq("12315678"),
    confirm_identity=seq("12315678"),
    identity_type="passport",
    is_dob_estimated="-",
    screening_identifier=uuid4(),
    site=Site.objects.get_current(),
)

aeinitial = Recipe(
    AeInitial,
    report_datetime=get_utcnow() - relativedelta(days=5),
    action_identifier=None,
    ae_description="A description of this event",
    ae_grade=GRADE4,
    ae_study_relation_possibility=YES,
    ae_start_date=get_utcnow().date() + relativedelta(days=5),
    ae_awareness_date=get_utcnow().date() + relativedelta(days=5),
    sae=NO,
    susar=NO,
    susar_reported=NOT_APPLICABLE,
    ae_cause=NO,
    ae_cause_other=None,
)

aetmg = Recipe(
    AeTmg,
    action_identifier=None,
    report_datetime=get_utcnow(),
)

aesusar = Recipe(
    AeSusar,
    action_identifier=None,
    report_datetime=get_utcnow(),
)

aefollowup = Recipe(
    AeFollowup,
    relevant_history=NO,
    action_identifier=None,
    report_datetime=get_utcnow(),
)


deathreport = Recipe(
    DeathReport,
    action_identifier=None,
    report_datetime=get_utcnow(),
    death_datetime=get_utcnow(),
)


deathreporttmg = Recipe(
    DeathReportTmg,
    action_identifier=None,
    report_datetime=get_utcnow(),
)


deathreporttmgsecond = Recipe(
    DeathReportTmgSecond,
    action_identifier=None,
    report_datetime=get_utcnow(),
)
