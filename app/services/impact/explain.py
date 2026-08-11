from typing import Any, Dict


class ExplainabilityEngine:
    def generate_explanation(self, impact_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates human-readable explanations from impact metrics.
        """
        observed = [
            m
            for m in impact_metrics.get("metrics", [])
            if m["evidence_type"] == "observed"
        ]
        estimated = [
            m
            for m in impact_metrics.get("metrics", [])
            if m["evidence_type"] == "estimated"
        ]

        queue_metric = next(
            (m for m in estimated if m["metric"] == "estimated_queue"), None
        )
        speed_metric = next(
            (m for m in observed if m["metric"] == "average_speed"), None
        )
        count_metric = next(
            (m for m in observed if m["metric"] == "vehicle_count"), None
        )

        queue_m = queue_metric["value"] if queue_metric else 0
        speed = speed_metric["value"] if speed_metric else 0
        count = count_metric["value"] if count_metric else 0

        reasons = []
        severity = "LOW"
        recommended_action = "Maintain current signal timing"

        if queue_m > 200:
            reasons.append(f"Queue length: {queue_m} m")
            severity = "HIGH"
        elif queue_m > 50:
            reasons.append(f"Queue length: {queue_m} m")
            severity = "MEDIUM"

        if 0 < speed < 20:
            reasons.append(f"Average speed dropped to {speed} km/h")
            severity = "HIGH"

        if count > 50:
            reasons.append(f"High traffic volume: {count} vehicles")

        if severity == "HIGH":
            recommended_action = "Extend green phase by 15 seconds"
        elif severity == "MEDIUM":
            recommended_action = "Extend green phase by 5 seconds"

        if not reasons:
            reasons.append("Normal traffic patterns detected.")

        return {
            "title": (
                f"🚦 Intervention Recommended"
                if severity != "LOW"
                else "🟢 Status Normal"
            ),
            "severity": severity,
            "reasons": reasons,
            "recommended_action": recommended_action,
            "confidence": 0.82,
        }


explainability_engine = ExplainabilityEngine()
