from dateutil.relativedelta import relativedelta
from django.conf import settings
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_utils import get_utcnow

consent_v1 = ConsentDefinition(
    "adverse_event_app.subjectconsentv1",
    version="1",
    start=getattr(
        settings,
        "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
        get_utcnow().replace(microsecond=0, second=0, minute=0, hour=0)
        - relativedelta(months=1),
    ),
    end=getattr(
        settings,
        "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
        get_utcnow().replace(microsecond=999999, second=59, minute=59, hour=11)
        + relativedelta(years=1),
    ),
    age_min=18,
    age_is_adult=18,
    age_max=110,
    gender=[MALE, FEMALE],
)

site_consents.register(consent_v1)
