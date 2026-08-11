import json
import os

import streamlit as st


def load_scenario(scenario_name: str):
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "scenarios")
    try:
        with open(
            os.path.join(base_path, f"{scenario_name}.json"), "r", encoding="utf-8"
        ) as f:
            return json.load(f)
    except Exception:
        return None


def render_replay_page(client):
    st.markdown("## 📽️ Incident Scenario Replay")
    st.markdown("---")

    st.info(
        "This interactive VCR mode demonstrates the full deterministic lifecycle of an AEGIS-Traffic intervention."
    )

    # Timeline scrubber
    step = st.select_slider(
        "**Scenario Timeline**",
        options=["T+0", "T+1", "T+2", "T+3", "T+4"],
        value="T+0",
    )

    st.markdown("---")

    if step == "T+0":
        st.subheader("🟢 T+0: Baseline Normal Traffic")
        st.caption("EVIDENCE: **OBSERVED** (Live Telemetry)")
        st.write(
            "Traffic is flowing normally at Intersection A-17. The intelligent controller is operating under standard dynamic timing plans."
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Current Queue", "45 m")
        c2.metric("Average Speed", "48 km/h")
        c3.metric("System Status", "NOMINAL")

    elif step == "T+1":
        st.subheader("🟢 T+1: Incident Detected")
        st.caption("EVIDENCE: **OBSERVED** (Live Telemetry & CCTV Fusion)")
        st.error(
            "🚨 ANOMALY TRIGGERED: High congestion detected due to stalled vehicle."
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Current Queue", "420 m", "833%")
        c2.metric("Average Speed", "18 km/h", "-62.5%")
        c3.metric("Detection Confidence", "94%")

    elif step == "T+2":
        st.subheader("🔵 T+2: Impact Quantified")
        st.caption("EVIDENCE: **ESTIMATED** (Queuing Theory Model)")
        st.write(
            "The system calculates the civic impact of the anomaly if left unaddressed."
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Estimated Delay", "7.8 min/vehicle")
        c2.metric("Idle Emissions Rate", "4.2 kg/min")
        c3.metric("Capacity Drop", "34%")

    elif step == "T+3":
        st.subheader("🟡 T+3: Intervention Simulated")
        st.caption("EVIDENCE: **SIMULATED** (Deterministic State Machine)")
        st.write(
            "AEGIS automatically generates and simulates an optimal signal intervention."
        )

        st.info(
            "💡 **RECOMMENDATION**: Extend Phase 2 Green by +15 seconds for next 5 cycles."
        )

        c1, c2 = st.columns(2)
        c1.metric("Projected Queue", "335 m", "-20.2%")
        c2.metric("Projected Delay", "5.9 min", "-24.4%")

    elif step == "T+4":
        st.subheader("🟢 T+4: Human Decision & Record")
        st.caption("EVIDENCE: **APPROVED** (Immutable Audit Log)")
        st.write(
            "A human operator reviews the simulated evidence and approves the intervention."
        )

        st.success(
            "✅ **ACTION**: Intervention Deployed successfully. Impact recorded to Civic Ledger."
        )

        c1, c2 = st.columns(2)
        c1.metric("Time Saved", "1.2 hours total")
        c2.metric("CO₂ Prevented", "4.1 kg")
