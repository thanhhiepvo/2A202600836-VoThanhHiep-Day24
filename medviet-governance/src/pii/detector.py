# src/pii/detector.py
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider

SUPPORTED_LANG = "vi"
PII_DTYPES = {"cccd": str, "so_dien_thoai": str}


def _normalize_value(column: str, value: str) -> str:
    value = str(value)
    if column == "so_dien_thoai" and value.isdigit():
        return value.zfill(10)
    if column == "cccd" and value.isdigit():
        return value.zfill(12)
    return value


def build_vietnamese_analyzer() -> AnalyzerEngine:
    """
    Xây dựng AnalyzerEngine với các recognizer tùy chỉnh cho VN.
    """
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\d{12}",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        patterns=[cccd_pattern],
        context=["cccd", "căn cước", "chứng minh", "cmnd"],
        supported_language=SUPPORTED_LANG,
    )

    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"0[35789]\d{8}",
            score=0.85
        )],
        context=["điện thoại", "sdt", "phone", "liên hệ"],
        supported_language=SUPPORTED_LANG,
    )

    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL_ADDRESS",
        patterns=[Pattern(
            name="email_pattern",
            regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            score=0.9
        )],
        supported_language=SUPPORTED_LANG,
    )

    vn_name_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        patterns=[Pattern(
            name="vn_name",
            regex=r"(?:[\wÀ-ỹ]+\s+){1,4}[\wÀ-ỹ]+",
            score=0.75
        )],
        supported_language=SUPPORTED_LANG,
    )

    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": SUPPORTED_LANG,
                    "model_name": "en_core_web_sm"}]
    })
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=[SUPPORTED_LANG])
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(email_recognizer)
    analyzer.registry.add_recognizer(vn_name_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """
    Detect PII trong text tiếng Việt.
    Entities: PERSON, EMAIL_ADDRESS, VN_CCCD, VN_PHONE
    """
    results = analyzer.analyze(
        text=text,
        language=SUPPORTED_LANG,
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
    )
    return results
