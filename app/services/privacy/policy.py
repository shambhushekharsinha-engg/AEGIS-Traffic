from typing import Dict, Any


class PrivacyPolicy:
    def __init__(self, privacy_mode_enabled: bool = True):
        self.privacy_mode_enabled = privacy_mode_enabled

    def redact_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redacts PII from telemetry data at the API boundary.
        """
        if not self.privacy_mode_enabled:
            return telemetry

        redacted = telemetry.copy()

        # Redact ANPR / Plates
        if "plate_number" in redacted:
            redacted["plate_number"] = None
        if "plate_confidence" in redacted:
            redacted["plate_confidence"] = None

        # Redact facial recognition / individuals if any
        if "face_id" in redacted:
            redacted["face_id"] = None

        redacted["privacy_mode"] = True
        return redacted

    def redact_response(self, data: Any) -> Any:
        """
        Recursively redacts PII from any API response structure.
        """
        if not self.privacy_mode_enabled:
            return data

        if isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                if k in [
                    "plate_number",
                    "plate_confidence",
                    "face_id",
                    "plate",
                    "license_plate",
                    "face_embedding",
                    "vehicle_owner",
                ]:
                    redacted[k] = None
                else:
                    redacted[k] = self.redact_response(v)
            redacted["privacy_mode"] = True
            return redacted
        elif isinstance(data, list):
            return [self.redact_response(item) for item in data]
        else:
            return data


privacy_policy = PrivacyPolicy()
