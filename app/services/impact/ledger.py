from typing import Any, Dict

from sqlalchemy.orm import Session

from app.db.models import DecisionRecord, IncidentLog


class ImpactLedgerService:
    @staticmethod
    def calculate_ledger(db: Session) -> Dict[str, Any]:
        """
        Calculates the Civic Impact Ledger, properly separating:
        1. OBSERVED - Actual telemetry
        2. ESTIMATED - Impact calculated from observed telemetry
        3. SIMULATED - Projected outcomes from what-if scenarios
        4. APPROVED - Human-approved interventions
        """
        # In a real deployed system, these would be robust SQL aggregations.
        # For the PBEL demonstration, we aggregate the deterministic DB states.

        # 1. OBSERVED
        total_incidents = db.query(IncidentLog).count()
        total_vehicles_observed = total_incidents * 85  # heuristic baseline for demo

        # 2. ESTIMATED
        # Calculated from observed incidents
        total_estimated_delay_hours = total_incidents * 2.4
        total_estimated_emissions_kg = total_incidents * 12.5

        # 3. SIMULATED
        # Any DecisionRecord that was evaluated
        total_simulations = db.query(DecisionRecord).count()
        projected_queue_reduction_meters = total_simulations * 45.5

        # 4. APPROVED
        approved_decisions = (
            db.query(DecisionRecord).filter(DecisionRecord.status == "APPROVED").all()
        )
        total_approved = len(approved_decisions)

        approved_time_saved_hours = 0.0
        approved_emissions_avoided_kg = 0.0

        for record in approved_decisions:
            # Safely extract from JSON simulation payload
            sim_data = record.simulation_payload or {}
            scenarios = sim_data.get("scenarios", [])
            for s in scenarios:
                if s.get("scenario_id") == record.scenario_id:
                    approved_time_saved_hours += s.get("projected_delay_savings", 1.2)
                    approved_emissions_avoided_kg += s.get(
                        "projected_emission_savings", 4.1
                    )
                    break

        # Illustrative Economic Value ($)
        # e.g., $15 per hour of travel time saved, $0.05 per kg CO2
        economic_value = (approved_time_saved_hours * 15.0) + (
            approved_emissions_avoided_kg * 0.05
        )

        return {
            "evidence_classification": {
                "OBSERVED": {
                    "description": "Actual raw telemetry",
                    "metrics": {
                        "incidents_detected": total_incidents,
                        "vehicles_processed": total_vehicles_observed,
                    },
                },
                "ESTIMATED": {
                    "description": "Calculated from observed baseline",
                    "metrics": {
                        "delay_hours": round(total_estimated_delay_hours, 1),
                        "idle_emissions_kg": round(total_estimated_emissions_kg, 1),
                    },
                },
                "SIMULATED": {
                    "description": "Projected outcomes from what-if models",
                    "metrics": {
                        "interventions_evaluated": total_simulations,
                        "potential_queue_reduction_m": round(
                            projected_queue_reduction_meters, 1
                        ),
                    },
                },
                "APPROVED": {
                    "description": "Human-approved intervention outcomes",
                    "metrics": {
                        "approved_count": total_approved,
                        "time_saved_hours": round(approved_time_saved_hours, 1),
                        "co2_avoided_kg": round(approved_emissions_avoided_kg, 1),
                        "illustrative_economic_value_usd": round(economic_value, 2),
                    },
                },
            }
        }
