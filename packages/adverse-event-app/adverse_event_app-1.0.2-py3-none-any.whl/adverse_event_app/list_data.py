from edc_constants.constants import (
    DEAD,
    MALIGNANCY,
    NOT_APPLICABLE,
    OTHER,
    TUBERCULOSIS,
    UNKNOWN,
)
from edc_constants.disease_constants import (
    ANAEMIA,
    BACTERAEMIA,
    BACTERIAL_PNEUMONIA,
    NEUTROPAENIA,
    PNEUMONIA,
    RENAL_IMPAIRMENT,
    THROMBOCYTOPENIA,
)

list_data = {
    "edc_adverse_event.causeofdeath": [
        (BACTERAEMIA, "Bacteraemia"),
        (BACTERIAL_PNEUMONIA, "Bacterial pneumonia"),
        (MALIGNANCY, "Malignancy"),
        ("art_toxicity", "ART toxicity"),
        ("IRIS_non_CM", "IRIS non-CM"),
        ("diarrhea_wasting", "Diarrhea/wasting"),
        (UNKNOWN, "Unknown"),
        (OTHER, "Other"),
    ],
    "edc_adverse_event.aeclassification": [
        (ANAEMIA, "Anaemia"),
        ("bacteraemia/sepsis", "Bacteraemia/Sepsis"),
        ("CM_IRIS", "CM IRIS"),
        ("diarrhoea", "Diarrhoea"),
        ("hypokalaemia", "Hypokalaemia"),
        (NEUTROPAENIA, "Neutropaenia"),
        (PNEUMONIA, "Pneumonia"),
        (RENAL_IMPAIRMENT, "Renal impairment"),
        ("respiratory_distress", "Respiratory distress"),
        (TUBERCULOSIS, "TB"),
        (THROMBOCYTOPENIA, "Thrombocytopenia"),
        ("thrombophlebitis", "Thrombophlebitis"),
        (OTHER, "Other"),
    ],
    "edc_adverse_event.saereason": [
        (NOT_APPLICABLE, "Not applicable"),
        (DEAD, "Death"),
        ("life_threatening", "Life-threatening"),
        ("significant_disability", "Significant disability"),
        (
            "in-patient_hospitalization",
            (
                "In-patient hospitalization or prolongation "
                "(17 or more days from study inclusion)"
            ),
        ),
        (
            "medically_important_event",
            "Medically important event (e.g. Severe thrombophlebitis, Bacteraemia, "
            "recurrence of symptoms not requiring admission, Hospital acquired "
            "pneumonia)",
        ),
    ],
}
