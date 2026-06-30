# src/quality/validation.py
import re
import pandas as pd

PII_DTYPES = {"cccd": str, "so_dien_thoai": str}
VALID_CONDITIONS = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def _load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=PII_DTYPES)


def _get_gx_validator(df: pd.DataFrame):
    import great_expectations as gx

    context = gx.get_context()
    ds_name = "patient_pandas"

    try:
        datasource = context.data_sources.add_pandas(ds_name)
    except Exception:
        datasource = context.data_sources.get(ds_name)

    asset_names = [asset.name for asset in datasource.assets]
    asset = (
        datasource.get_asset("patients")
        if "patients" in asset_names
        else datasource.add_dataframe_asset(name="patients")
    )

    batch_definitions = list(asset.batch_definitions)
    batch_definition = (
        batch_definitions[0]
        if batch_definitions
        else asset.add_batch_definition_whole_dataframe("whole")
    )

    return context.get_validator(
        batch_request=batch_definition.build_batch_request(
            batch_parameters={"dataframe": df}
        )
    )


def build_patient_expectation_suite():
    """Tạo và lưu expectation suite cho patient data (Great Expectations 1.x)."""
    import great_expectations as gx

    df = _load_csv("data/raw/patients_raw.csv")
    validator = _get_gx_validator(df)

    validator.expect_column_values_to_not_be_null("patient_id")
    validator.expect_column_value_lengths_to_equal("cccd", 12)
    validator.expect_column_values_to_be_between(
        "ket_qua_xet_nghiem", min_value=0, max_value=50
    )
    validator.expect_column_values_to_be_in_set("benh", VALID_CONDITIONS)
    validator.expect_column_values_to_match_regex("email", EMAIL_REGEX)
    validator.expect_column_values_to_be_unique("patient_id")

    suite = validator.get_expectation_suite()
    suite.name = "patient_data_suite"
    context = gx.get_context()
    context.suites.add(suite)

    validation_result = validator.validate()
    return {
        "suite_name": suite.name,
        "expectation_count": len(suite.expectations),
        "success": validation_result.success,
    }


def validate_raw_patient_data(filepath: str = "data/raw/patients_raw.csv") -> dict:
    """Chạy expectation suite trên raw patient data."""
    df = _load_csv(filepath)
    validator = _get_gx_validator(df)
    result = validator.validate()

    failed = [
        exp["expectation_config"]["type"]
        for exp in result.results
        if not exp.success
    ]

    return {
        "success": result.success,
        "failed_checks": failed,
        "stats": {"total_rows": len(df), "columns": list(df.columns)},
    }


def validate_anonymized_data(filepath: str) -> dict:
    df = _load_csv(filepath)
    original_df = _load_csv("data/raw/patients_raw.csv")

    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        },
    }

    important_cols = ["patient_id", "ho_ten", "cccd", "email", "benh"]
    for col in important_cols:
        if col in df.columns and df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Null values found in column '{col}'")

    if "cccd" in df.columns and "cccd" in original_df.columns:
        leaked = set(original_df["cccd"].astype(str)) & set(df["cccd"].astype(str))
        if leaked:
            results["success"] = False
            results["failed_checks"].append(
                f"Original CCCD values still present: {len(leaked)} leaked"
            )

    if len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append(
            f"Row count mismatch: anonymized={len(df)}, original={len(original_df)}"
        )

    if not df["email"].astype(str).str.match(EMAIL_REGEX).all():
        results["success"] = False
        results["failed_checks"].append("email format invalid after anonymization")

    return results
