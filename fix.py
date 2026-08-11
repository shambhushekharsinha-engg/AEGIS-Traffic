import re

with open('dashboard/views/impact.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove the mojibake inserted earlier just in case
code = re.sub(r'def render_impact_ledger.*?def load_scenario', 'def load_scenario', code, flags=re.DOTALL)
# Remove the old render call
code = code.replace('    render_impact_ledger(client)\n', '')

ledger_code = """
def render_impact_ledger(client):
    st.markdown("### 🌍 Civic Impact Ledger")
    try:
        response = client.get("/api/v1/oversight/ledger")
        if response.status_code == 200:
            ledger = response.json().get("evidence_classification", {})
            
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.info("**🟢 OBSERVED**\\n\\nActual Telemetry")
                obs = ledger.get("OBSERVED", {}).get("metrics", {})
                st.metric("Incidents Detected", obs.get("incidents_detected", 0))
                st.metric("Vehicles Processed", obs.get("vehicles_processed", 0))
                
            with c2:
                st.info("**🔵 ESTIMATED**\\n\\nCalculated Impact")
                est = ledger.get("ESTIMATED", {}).get("metrics", {})
                st.metric("Delay (Hours)", est.get("delay_hours", 0.0))
                st.metric("Idle CO₂ (kg)", est.get("idle_emissions_kg", 0.0))
                
            with c3:
                st.warning("**🟡 SIMULATED**\\n\\nProjected Outcomes")
                sim = ledger.get("SIMULATED", {}).get("metrics", {})
                st.metric("Interventions Evaluated", sim.get("interventions_evaluated", 0))
                st.metric("Queue Reduction", f"{sim.get('potential_queue_reduction_m', 0.0)}m")
                
            with c4:
                st.success("**🟢 APPROVED**\\n\\nRecorded Decisions")
                appr = ledger.get("APPROVED", {}).get("metrics", {})
                st.metric("Approved Interventions", appr.get("approved_count", 0))
                st.metric("Illustrative Econ Value", f"${appr.get('illustrative_economic_value_usd', 0.0):,.2f}")
                
            st.markdown("---")
    except Exception as e:
        logger.error(f"Failed to load Impact Ledger: {e}")
"""

code = re.sub(r'def render_impact_dashboard\(client\):', ledger_code + '\ndef render_impact_dashboard(client):\n    render_impact_ledger(client)\n', code)

with open('dashboard/views/impact.py', 'w', encoding='utf-8') as f:
    f.write(code)
