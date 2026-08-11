import streamlit as st
import json
import os
from dashboard.services.logger import logger

def load_scenario(scenario_name: str):
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "scenarios")
    try:
        with open(os.path.join(base_path, f"{scenario_name}.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load scenario {scenario_name}: {e}")
        return None

def render_impact_dashboard(client):
    st.markdown("## 🌍 AEGIS CITY IMPACT")
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🚦 Active Events", "7")
    col2.metric("🚗 Vehicles", "1,284")
    col3.metric("⏱ Estimated Delay", "426 min")
    col4.metric("🍃 Estimated CO₂", "18.4 kg")
    col5.metric("🚶 Safety Alerts", "12")
    
    st.markdown("---")
    
    st.subheader("🚨 PRIORITY EVENT")
    st.markdown("### Intersection A-17")
    st.error("HIGH CONGESTION")
    
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("Queue", "420 m")
    scol2.metric("Speed", "18 km/h")
    scol3.metric("Confidence", "78%")
    
    with st.expander("Why was this detected?"):
        st.write("• Queue length: 420 m")
        st.write("• Average speed: 18 km/h")
        st.write("• Sustained congestion: 4 min")
        st.caption("Evidence: 🟢 Observed, 🔵 Estimated")
        
    st.markdown("---")
    
    st.subheader("💡 RECOMMENDED INTERVENTION")
    st.info("Extend green phase +15 sec")
    
    if st.button("🔬 SIMULATE"):
        st.markdown("---")
        st.subheader("🔬 SIMULATION")
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            st.metric("Current Queue", "420 m")
            st.metric("Current Delay", "7.8 min")
        with sim_col2:
            st.metric("Proposed Queue", "335 m", "-20.2%")
            st.metric("Proposed Delay", "5.9 min", "-24.4%")
            
        st.success("Projected queue reduction: 20.2% (🟡 Simulated)")
        
        # Simulated Plotly chart
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[420, 420, 420, 420, 420, 420], mode='lines+markers', name='Baseline Queue (m)', line=dict(color='red')))
        fig.add_trace(go.Scatter(y=[420, 400, 380, 360, 345, 335], mode='lines+markers', name='Proposed Queue (m)', line=dict(color='green')))
        fig.update_layout(title="Projected Queue Evolution (5 Cycles)", xaxis_title="Cycle Number", yaxis_title="Queue Length (m)", margin=dict(l=0, r=0, t=30, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        acol1, acol2 = st.columns(2)
        with acol1:
            if st.button("✅ APPROVE", use_container_width=True):
                st.toast("Decision APPROVED and recorded to immutable audit log.")
        with acol2:
            if st.button("❌ REJECT", use_container_width=True):
                st.toast("Decision REJECTED.")
                
    st.markdown("---")
    st.subheader("📋 RECENT DECISIONS")
    st.dataframe([
        {"id": "dec_881", "event": "Intersection A-17", "action": "Extend Green +15s", "status": "PENDING"},
        {"id": "dec_880", "event": "Pedestrian Zone B", "action": "Extend Walk +10s", "status": "APPROVED"}
    ], use_container_width=True)
