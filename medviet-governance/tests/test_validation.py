# tests/test_validation.py
from src.quality.validation import (
    build_patient_expectation_suite,
    validate_anonymized_data,
    validate_raw_patient_data,
)


def test_build_patient_expectation_suite():
    result = build_patient_expectation_suite()
    assert result["success"] is True
    assert result["expectation_count"] >= 6


def test_validate_raw_patient_data():
    result = validate_raw_patient_data("data/raw/patients_raw.csv")
    assert result["success"] is True
    assert result["stats"]["total_rows"] == 200


def test_validate_anonymized_data():
    result = validate_anonymized_data("data/processed/patients_anonymized.csv")
    assert result["success"] is True
