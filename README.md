<div align="center">

<img src="https://img.shields.io/badge/AEGIS%20TRAFFIC-v10.0%20PRODUCTION-00f0ff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzAwZjBmZiIgZD0iTTEyIDJMMiA3bDEwIDUgMTAtNXoiLz48cGF0aCBmaWxsPSIjMDBmMGZmIiBkPSJNMiAxN2wxMCA1IDEwLTV2LTZMMTIgMTYgMiAxMXoiLz48L3N2Zz4=&labelColor=010308" />

# 🚦 AEGIS — Traffic
### **AI-Powered Civic Traffic Intelligence**

<br/>

> *An end-to-end traffic intelligence system that detects real-world road conditions, quantifies their impact, explains why an intervention is recommended, allows operators to simulate that intervention, records human decisions, and demonstrates measurable performance at scale.*

<br/>

</div>

---

## 🌍 The Civic Problem

Modern cities face enormous challenges in managing urban mobility. AEGIS-Traffic addresses these critical issues:
- **Congestion**: Accurately detecting traffic buildup and proactively responding to alleviate gridlock.
- **Emergency/Incident Response**: Instantly identifying accidents or blocked lanes and estimating their ripple effect on surrounding traffic.
- **Pedestrian Safety**: Protecting vulnerable road users (VRUs) by adjusting signal phases when pedestrian density is dangerously high.
- **Privacy Concerns**: Implementing intelligent monitoring without sacrificing citizen privacy, ensuring compliance and trust.

## 💡 What AEGIS-Traffic Does

AEGIS transforms raw camera feeds into a complete civic-impact workflow:

**Detect** → **Understand** → **Quantify Impact** → **Recommend** → **Simulate** → **Human Approval** → **Audit**

---

## 🎬 Reproducible Civic Impact Demo

AEGIS comes with a reproducible, deterministic demo framework. You can run these scenarios locally without needing a live camera feed:

1. `01_congestion.json` - High traffic volume and sustained queues.
2. `02_pedestrian_risk.json` - High pedestrian density at crosswalks.
3. `03_incident_response.json` - Accident detected blocking a lane.
4. `04_normal_traffic.json` - Baseline, free-flowing traffic.

*These scenarios provide predictable JSON telemetry to demonstrate the end-to-end impact assessment and simulation engine.*

---

## 🌍 City Impact Dashboard

The centerpiece of AEGIS is the **City Impact Dashboard**. Instead of presenting a collection of disconnected charts, the dashboard tells a complete story:

1. **Event Detected**: "Intersection A-17: HIGH CONGESTION"
2. **Impact Quantified**: Estimates delay per vehicle and idle emissions.
3. **Recommendation**: "Extend green phase +15 sec"
4. **Simulation**: Projects the exact queue reduction (-20.2%) deterministically.
5. **Approval**: Operator clicks "Approve", committing the decision to the immutable audit log.

---

## 🔬 Deterministic What-If Simulation

AEGIS goes beyond "AI prediction" by incorporating a **Deterministic Mathematical Simulator**:
- **Queue Model**: Uses arrival rate (λ) and service rate (μ) to project traffic state evolution.
- **Multi-Scenario Comparison**: Compare `Current` vs `+10s` vs `+15s` interventions side-by-side.
- **Determinism**: Identical inputs guarantee identical simulation outputs.
- **Non-destructive**: Running simulations does not mutate the production traffic state in the database.

---

## 🧑‍⚖️ Human-in-the-Loop Governance

AEGIS-Traffic is designed to assist humans, not bypass them. 

- **Oversight API**: Interventions follow a strict `PENDING → APPROVED / REJECTED` lifecycle.
- **Durable PostgreSQL Audit Trail**: Every decision is persisted as a `DecisionRecord` with reviewer identity, reason, and simulation references.
- **Explainable Decision Cards**: Human-readable explanations ("Why was this detected? -> Lane occupancy: 87%") accompany every AI recommendation.

---

## 🔐 Privacy by Design

Privacy is enforced at the API boundary, not just toggled on the frontend.
- **API-Boundary Redaction**: The backend `PrivacyPolicy` physically strips PII (`plate_number`, `face_id`, `face_embedding`) from the JSON responses.
- **Idempotent Enforcement**: The redaction engine is mathematically idempotent (`redact(redact(data)) == redact(data)`).
- **Protection by Default**: Prevents accidental leakage of citizen data to unauthorized dashboard clients.

---

## 📊 Verified Engineering Evidence

*Note: AEGIS-Traffic is production-ready at the tested scale. The following metrics are median/representative results verified from three independent Locust load-testing executions.*

| Metric | Result |
|:---|:---|
| **API p95 Latency** | `44 ms` |
| **2-worker efficiency** | `95.8%` |
| **3-worker efficiency** | `93.7%` |
| **Baseline throughput** | `4.8 TPS` |
| **3-worker throughput** | `13.5 TPS` |
| **HTTP 5xx Errors** | `0` |
| **HTTP 502/503 Errors** | `0` |
| **Infrastructure crashes** | `0` |

---

## 🧪 Engineering Validation

AEGIS features a robust suite of invariant tests to guarantee reliability and civic safety:
- **Determinism**: Asserts simulations yield identical projections.
- **Non-destructive**: Ensures simulation never overwrites production telemetry.
- **Privacy**: Verifies that `privacy_mode=True` completely redacts PII elements.
- **Governance**: Tests state transition integrity (e.g., `APPROVED` cannot be flipped to `REJECTED`).
- **Impact Calculations**: Verifies correct mathematical estimates of emissions and delays.

---

## 🏗️ Architecture

```text
       Streamlit Dashboard
                ↓
           FastAPI Backend
                ↓
┌───────────────┬────────────────┐
│ Impact Engine │ Simulation     │
│ Privacy       │ Governance     │
└───────────────┴────────────────┘
                ↓
         PostgreSQL Database
                ↓
        AI / Inference Layer (YOLO)
```

---

## 📁 Project Structure

```text
AEGIS-Traffic/
├── app/               # FastAPI backend (Models, Routers, Core Logic)
├── dashboard/         # Streamlit frontend (City Impact, Operations HUD)
├── demo/              # Reproducible civic impact scenarios
├── tests/             # Invariant testing (Privacy, Simulation, Governance)
└── README.md          # You are here
```

---

## 🚀 Running Locally

1. Clone the repository: `git clone https://github.com/shambhushekharsinha-engg/AEGIS-Traffic.git`
2. Start the database and backend: `docker-compose up -d`
3. Launch the dashboard: `cd dashboard && streamlit run app.py`

---

## ⚠️ Evidence & Limitations

AEGIS explicitly distinguishes between different levels of data confidence via the **Impact Contract**. These distinctions are visible throughout the UI:

- 🟢 **Observed**: Directly measured from the camera/system (e.g., `127 vehicles detected`).
- 🔵 **Estimated**: Calculated heuristically from observed data (e.g., `Estimated queue: 420 m`).
- 🟡 **Simulated**: Projected mathematically by the intervention model (e.g., `Queue reduction: -20%`).
- ⚪ **External validation**: Verified against independent sensors/datasets.

*Disclaimer: Unless independently validated against real-world civic deployments, all emissions, travel-time savings, and simulation outcomes are **estimates** dependent on configurable assumptions.*

---

## 🔮 Future Work

- Integration with **Redis** for distributed simulation state caching.
- Asynchronous inference optimization for ultra-high concurrency.
- Validation of impact models against real municipal traffic datasets.
- Field trials to gather ⚪ *External Validation* metrics.