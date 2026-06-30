# src/pii/anonymizer.py
import random
import pandas as pd
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
from .detector import build_vietnamese_analyzer, detect_pii, _normalize_value

fake = Faker("vi_VN")


def _fake_cccd() -> str:
    return str(random.randint(0, 9)) + "".join(str(random.randint(0, 9)) for _ in range(11))


def _fake_phone() -> str:
    return f"0{random.choice([3, 5, 7, 8, 9])}" + "".join(
        str(random.randint(0, 9)) for _ in range(8)
    )


class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        operators = {}

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", {"new_value": _fake_cccd()}),
                "VN_PHONE": OperatorConfig("replace", {"new_value": _fake_phone()}),
            }
        elif strategy == "mask":
            operators = {
                "PERSON": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 100, "from_end": False}),
                "EMAIL_ADDRESS": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 100, "from_end": False}),
                "VN_CCCD": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 8, "from_end": False}),
                "VN_PHONE": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 6, "from_end": False}),
            }
        elif strategy == "hash":
            operators = {
                entity: OperatorConfig("hash", {"hash_type": "sha256"})
                for entity in ["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
            }

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        for col in ["ho_ten", "dia_chi", "email", "bac_si_phu_trach"]:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].apply(
                    lambda x: self.anonymize_text(str(x), "replace")
                )

        if "cccd" in df_anon.columns:
            df_anon["cccd"] = [_fake_cccd() for _ in range(len(df_anon))]

        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = [_fake_phone() for _ in range(len(df_anon))]

        return df_anon

    def calculate_detection_rate(
        self,
        original_df: pd.DataFrame,
        pii_columns: list
    ) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].astype(str):
                total += 1
                normalized = _normalize_value(col, value)
                results = detect_pii(normalized, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0
