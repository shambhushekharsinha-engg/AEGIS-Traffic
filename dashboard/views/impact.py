import json
import os

import pandas as pd
import streamlit as st

from dashboard.services.logger import logger


def load_scenario(scenario_name: str):
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "scenarios")
    try:
        with open(os.path.join(base_path, f"{scenario_name}.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load scenario {scenario_name}: {e}")
        return None


def render_impact_ledger(client):
    st.markdown("### 🌍 Civic Impact Ledger")
    try:
        response = client.get("/api/v1/oversight/ledger")
        if response.status_code == 200:
            ledger = response.json().get("evidence_classification", {})

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.info("**🟢 OBSERVED**\n\nActual Telemetry")
                obs = ledger.get("OBSERVED", {}).get("metrics", {})
                st.metric("Incidents Detected", obs.get("incidents_detected", 0))
                st.metric("Vehicles Processed", obs.get("vehicles_processed", 0))

            with c2:
                st.info("**🔵 ESTIMATED**\n\nCalculated Impact")
                est = ledger.get("ESTIMATED", {}).get("metrics", {})
                st.metric("Delay (Hours)", est.get("delay_hours", 0.0))
                st.metric("Idle CO₂ (kg)", est.get("idle_emissions_kg", 0.0))

            with c3:
                st.warning("**🟡 SIMULATED**\n\nProjected Outcomes")
                sim = ledger.get("SIMULATED", {}).get("metrics", {})
                st.metric(
                    "Interventions Evaluated", sim.get("interventions_evaluated", 0)
                )
                st.metric(
                    "Queue Reduction", f"{sim.get('potential_queue_reduction_m', 0.0)}m"
                )

            with c4:
                st.success("**🟢 APPROVED**\n\nRecorded Decisions")
                appr = ledger.get("APPROVED", {}).get("metrics", {})
                st.metric("Approved Interventions", appr.get("approved_count", 0))
                st.metric(
                    "Illustrative Econ Value",
                    f"${appr.get('illustrative_economic_value_usd', 0.0):,.2f}",
                )

            st.markdown("---")
    except Exception as e:
        logger.error(f"Failed to load Impact Ledger: {e}")


def render_impact_dashboard(client):
    render_impact_ledger(client)

    st.markdown("## ðŸŒ  AEGIS CITY IMPACT")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("ðŸš¦ Active Events", "7")
    col2.metric("ðŸš— Vehicles", "1,284")
    col3.metric("â ± Estimated Delay", "426 min")
    col4.metric("ðŸ ƒ Estimated COâ‚‚", "18.4 kg")
    col5.metric("ðŸš¶ Safety Alerts", "12")

    st.markdown("---")

    st.subheader("ðŸš¨ PRIORITY EVENT")
    st.markdown("### Intersection A-17")
    st.error("HIGH CONGESTION")

    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("Queue", "420 m")
    scol2.metric("Speed", "18 km/h")
    scol3.metric("Confidence", "78%")

    with st.expander("Why was this detected?"):
        st.write("â€¢ Queue length: 420 m")
        st.write("â€¢ Average speed: 18 km/h")
        st.write("â€¢ Sustained congestion: 4 min")
        st.caption("Evidence: ðŸŸ¢ Observed, ðŸ”µ Estimated")

    st.markdown("---")

    st.subheader("ðŸ’¡ RECOMMENDED INTERVENTION")
    st.info("Extend green phase +15 sec")

    if st.button("ðŸ”¬ SIMULATE"):
        st.markdown("---")
        st.subheader("ðŸ”¬ SIMULATION")

        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            st.metric("Current Queue", "420 m")
            st.metric("Current Delay", "7.8 min")
        with sim_col2:
            st.metric("Proposed Queue", "335 m", "-20.2%")
            st.metric("Proposed Delay", "5.9 min", "-24.4%")

        st.success("Projected queue reduction: 20.2% (ðŸŸ¡ Simulated)")

        # Simulated Plotly chart
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                y=[420, 420, 420, 420, 420, 420],
                mode="lines+markers",
                name="Baseline Queue (m)",
                line=dict(color="red"),
            )
        )
        fig.add_trace(
            go.Scatter(
                y=[420, 400, 380, 360, 345, 335],
                mode="lines+markers",
                name="Proposed Queue (m)",
                line=dict(color="green"),
            )
        )
        fig.update_layout(
            title="Projected Queue Evolution (5 Cycles)",
            xaxis_title="Cycle Number",
            yaxis_title="Queue Length (m)",
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

        acol1, acol2 = st.columns(2)
        with acol1:
            if st.button("âœ… APPROVE", use_container_width=True):
                st.toast("Decision APPROVED and recorded to immutable audit log.")
        with acol2:
            if st.button("âŒ REJECT", use_container_width=True):
                st.toast("Decision REJECTED.")

    st.markdown("---")
    st.subheader("ðŸ“‹ RECENT DECISIONS")
    st.dataframe(
        [
            {
                "id": "dec_881",
                "event": "Intersection A-17",
                "action": "Extend Green +15s",
                "status": "PENDING",
            },
            {
                "id": "dec_880",
                "event": "Pedestrian Zone B",
                "action": "Extend Walk +10s",
                "status": "APPROVED",
            },
        ],
        use_container_width=True,
    )
