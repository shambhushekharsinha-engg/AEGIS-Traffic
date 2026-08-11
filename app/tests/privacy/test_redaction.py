import pytest
from app.services.privacy.policy import PrivacyPolicy


def test_privacy_redaction_removes_pii():
    policy = PrivacyPolicy(privacy_mode_enabled=True)

    raw_telemetry = {
        "vehicle_count": 5,
        "average_speed": 40.5,
        "plate_number": "XYZ-1234",
        "plate_confidence": 0.98,
        "face_id": "face_99812",
        "color": "red",
    }

    redacted = policy.redact_telemetry(raw_telemetry)

    assert (
        redacted["plate_number"] is None
    ), "Plate number must be None when privacy is enabled."
    assert (
        redacted["plate_confidence"] is None
    ), "Plate confidence must be None when privacy is enabled."
    assert redacted["face_id"] is None, "Face ID must be None when privacy is enabled."
    assert (
        redacted.get("privacy_mode") is True
    ), "Telemetry must be flagged as privacy_mode=True."
    assert redacted["color"] == "red", "Non-PII fields should be preserved."


def test_privacy_disabled_preserves_pii():
    policy = PrivacyPolicy(privacy_mode_enabled=False)

    raw_telemetry = {"plate_number": "XYZ-1234"}

    preserved = policy.redact_telemetry(raw_telemetry)
    assert (
        preserved["plate_number"] == "XYZ-1234"
    ), "Plate number must be preserved when privacy is disabled."


def test_privacy_idempotency():
    policy = PrivacyPolicy(privacy_mode_enabled=True)
    raw_telemetry = {"plate_number": "XYZ-1234", "color": "red"}

    redacted_once = policy.redact_telemetry(raw_telemetry)
    redacted_twice = policy.redact_telemetry(redacted_once)

    assert (
        redacted_once == redacted_twice
    ), "Redact should be idempotent: redact(redact(data)) == redact(data)"
