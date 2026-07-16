<div align="center">

<img src="https://img.shields.io/badge/AEGIS%20TRAFFIC-v7.0%20PRODUCTION-00f0ff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzAwZjBmZiIgZD0iTTEyIDJMMiA3bDEwIDUgMTAtNXoiLz48cGF0aCBmaWxsPSIjMDBmMGZmIiBkPSJNMiAxN2wxMCA1IDEwLTV2LTZMMTIgMTYgMiAxMXoiLz48L3N2Zz4=&labelColor=010308" />

# 🚦 AEGIS — Traffic
### **Adaptive Edge-Grade Intelligence System for Smart-City Traffic Management**

### 🌐 Live Deployment

[![Live Demo](https://img.shields.io/badge/🚀%20LIVE%20DEMO-aegis--traffic.vercel.app-00f0ff?style=for-the-badge&labelColor=010308)](https://aegis-traffic.vercel.app)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-purple?style=flat-square&logo=yolo&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyTorch-2.2+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black"/>
  <img src="https://img.shields.io/badge/SQLite-AES--256%20Encrypted-003B57?style=flat-square&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/JWT-HMAC--SHA256-black?style=flat-square&logo=jsonwebtokens&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-10b981?style=flat-square"/>
  <img src="https://img.shields.io/badge/Tests-6%2F6%20PASSING-10b981?style=flat-square&logo=pytest&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-PRODUCTION%20READY-00f0ff?style=flat-square"/>
</p>

<br/>

> **AEGIS-Traffic** is an industrial-grade, AI-powered smart city traffic management platform that fuses **computer vision (YOLOv8)**, **acoustic anomaly detection (FFT)**, and **zero-shot NLP (DistilBERT / Qwen 2.5)** into a real-time multimodal decision engine — secured end-to-end with AES-256 encryption, JWT authentication, and role-based access control.

<br/>

---

</div>

## 📋 Table of Contents

- [🏗️ Architecture Overview](#️-architecture-overview)
- [✨ Core Feature Matrix](#-core-feature-matrix)
- [🖥️ Live Platform Screenshots](#️-live-platform-screenshots)
- [⚙️ Technology Stack](#️-technology-stack)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [🔐 Security Architecture](#-security-architecture)
- [🤖 AI Fusion Pipeline](#-ai-fusion-pipeline)
- [⚙️ Operating Modes](#️-operating-modes)
- [📂 Project Structure](#-project-structure)
- [🧪 Test Suite](#-test-suite)
- [🌍 Geographic Registry](#-geographic-registry)
- [🤖 AI Copilot Assistant](#-ai-copilot-assistant)
- [📈 Analytics & Dataset Analyzer](#-analytics--dataset-analyzer)
- [📖 API Reference](#-api-reference)
- [🛠️ Configuration & Environment](#️-configuration--environment)
- [📜 License](#-license)

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                     AEGIS-TRAFFIC  v7.0                                │
│                SMART CITY OPERATIONS PLATFORM                          │
├──────────────────────────┬─────────────────────────────────────────────┤
│   STREAMLIT FRONTEND     │          FASTAPI BACKEND                    │
│   dashboard/app.py       │          app/main.py                        │
│                          │                                             │
│  ┌─────────────────────┐ │  ┌──────────────────────────────────────┐  │
│  │  Zero-Trust Login   │ │  │  JWT Auth + PBKDF2 Vault            │  │
│  │  Role Badge Portal  │─┼─▶│  /api/v1/auth/login                 │  │
│  └─────────────────────┘ │  │  /api/v1/auth/register              │  │
│  ┌─────────────────────┐ │  └──────────────────────────────────────┘  │
│  │  Operations HUD     │ │  ┌──────────────────────────────────────┐  │
│  │  Signal Controller  │─┼─▶│  Multimodal Fusion Engine           │  │
│  │  Acoustic Waveform  │ │  │  /api/v1/analyze                    │  │
│  └─────────────────────┘ │  │  ┌──────────┐ ┌────────┐ ┌───────┐ │  │
│  ┌─────────────────────┐ │  │  │ YOLOv8   │ │  FFT   │ │ NLP   │ │  │
│  │  Analytics Suite    │─┼─▶│  │ Vision   │ │ Audio  │ │Fusion │ │  │
│  │  Map Intelligence   │ │  │  └──────────┘ └────────┘ └───────┘ │  │
│  └─────────────────────┘ │  └──────────────────────────────────────┘  │
│  ┌─────────────────────┐ │  ┌──────────────────────────────────────┐  │
│  │  AI Copilot Chat    │─┼─▶│  Qwen 2.5 LLM Guardrailed Chat     │  │
│  └─────────────────────┘ │  │  /api/v1/chat                       │  │
│  ┌─────────────────────┐ │  └──────────────────────────────────────┘  │
│  │  Security Ledger    │─┼─▶│  AES-256 Encrypted SQLite Vault     │  │
│  │  Dataset Analyzer   │ │  │  /api/v1/history  (Admin/Auditor)   │  │
│  └─────────────────────┘ │  └──────────────────────────────────────┘  │
└──────────────────────────┴─────────────────────────────────────────────┘
```

---

## ✨ Core Feature Matrix

| Category | Feature | Implementation |
|---|---|---|
| 🤖 **AI Vision** | Real-time vehicle detection | YOLOv8-Nano / YOLOv8-XL COCO detection |
| 🔊 **Acoustics** | Sound anomaly detection | RMS dB measurement + FFT frequency analysis |
| 🧠 **NLP Fusion** | Context classification | DistilBERT zero-shot MNLI (Hugging Face) |
| 💬 **AI Copilot** | Traffic advisory chatbot | Qwen 2.5 with prompt-injection guardrails |
| 🔒 **Auth** | Zero-trust authentication | JWT HMAC-SHA256 + PBKDF2-SHA256 (100k iter) |
| 🛡️ **Encryption** | Database vault | Fernet AES-256-CBC + HMAC-SHA256 |
| 👥 **RBAC** | Role-based clearance | Admin / Operator / Auditor tiers |
| 🌍 **Geo** | Global site initialization | Nominatim OSM geocoding + simulated fallback |
| 🗺️ **Mapping** | Global incident registry | Plotly Mapbox dark-mode scatter map |
| ⚙️ **Modes** | 4-state operating modes | AI Auto / Manual Override / Lockdown / Predictive |
| 📈 **Analytics** | Production telemetry | Plotly: area, bar, scatter, pie, box, histogram |
| 📂 **Data Upload** | Custom dataset analyzer | CSV / Excel / JSON + 7 chart types + AI insights |
| 🧪 **Sandbox** | Offline scenario testing | Custom sensor parameter simulation |
| 📖 **Knowledge** | Diagnostic manual | 7 problem profiles with root cause & mitigations |
| 📚 **Learning** | Interactive guide | Step-by-step platform onboarding system |
| 📥 **Export** | Audit ledger download | Decrypted CSV export (Admin / Auditor only) |
| 🪝 **Webhooks** | First responder alerts | HTTP POST dispatch to municipal hubs |

---

## 🖥️ Live Platform Screenshots

### 🔐 Authentication Portal

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Zero-Trust Authentication Deck.png" alt="Zero-Trust Login" width="100%"/>
      <br/><sub><b>Zero-Trust Authentication Deck</b></sub>
      <br/><sub>JWT-secured login with role clearance badges and credential vault</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/User Registration Gateway.png" alt="User Registration" width="100%"/>
      <br/><sub><b>Operator Registration Gateway</b></sub>
      <br/><sub>Secure operator registration with PBKDF2-SHA256 password hashing</sub>
    </td>
  </tr>
</table>

---

### 📊 Operations HUD

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Initial Operations HUD State.png" alt="HUD Initial" width="100%"/>
      <br/><sub><b>Initial HUD — Sensor Grid Online</b></sub>
      <br/><sub>Boot screen awaiting scenario scan initialization</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Multimodal Telemetry Core Operations Cockpit.png" alt="Operations Cockpit" width="100%"/>
      <br/><sub><b>Multimodal Telemetry Operations Cockpit</b></sub>
      <br/><sub>Live YOLOv8 feed, signal controller, waveform analysis & advisory</sub>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <img src="Project Demo/screenshots/Adaptive Signal Controller & Real-Time Advisory Module.png" alt="Signal Controller" width="100%"/>
      <br/><sub><b>Adaptive Signal Controller & Real-Time Advisory Module</b></sub>
      <br/><sub>Phase-aware signal state machine with live rerouting advisories and acoustic telemetry</sub>
    </td>
  </tr>
</table>

---

### 📈 Analytics Suite

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Cryptographic Analytics Suite Upper Deck.png" alt="Analytics Upper" width="100%"/>
      <br/><sub><b>Production Analytics — Upper Deck</b></sub>
      <br/><sub>KPI tiles, Hazard Index time-series, Mode distribution pie chart</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Systemic Telemetry Analytics Lower Deck.png" alt="Analytics Lower" width="100%"/>
      <br/><sub><b>Systemic Telemetry Analytics — Lower Deck</b></sub>
      <br/><sub>Vehicle volume bars, latency scatter, scenario frequency & signal distribution</sub>
    </td>
  </tr>
</table>

---

### 🌍 Map Intelligence

<table>
  <tr>
    <td align="center" colspan="2">
      <img src="Project Demo/screenshots/Geographic Smart-City Node Intelligence Grid.png" alt="Map Intelligence" width="80%"/>
      <br/><sub><b>Geographic Smart-City Node Intelligence Grid</b></sub>
      <br/><sub>Global incident registry plotted on a dark-mode Mapbox canvas with risk-score colour scaling</sub>
    </td>
  </tr>
</table>

---

### 🤖 AI Copilot

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Guardrailed AI Traffic Operations Copilot.png" alt="AI Copilot" width="100%"/>
      <br/><sub><b>Guardrailed AI Traffic Operations Copilot</b></sub>
      <br/><sub>Qwen 2.5 chatbot with 6-category prompt injection firewall</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Dynamic AI Chat History & Security Guardrails.png" alt="Chat History" width="100%"/>
      <br/><sub><b>Dynamic Chat History & Security Guardrails</b></sub>
      <br/><sub>Persistent session memory, quick-prompt buttons, and role-aware responses</sub>
    </td>
  </tr>
</table>

---

### 🧪 Sandbox & Simulation

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Multimodal Telemetry Simulation Sandbox.png" alt="Sandbox" width="100%"/>
      <br/><sub><b>Multimodal Telemetry Simulation Sandbox</b></sub>
      <br/><sub>Custom vehicle count, dB SPL, frequency, camera integrity & weather inputs</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Operational Diagnostics & Mitigation Manual.png" alt="Diagnostics" width="100%"/>
      <br/><sub><b>Operational Diagnostics & Mitigation Manual</b></sub>
      <br/><sub>7 problem profiles — root causes, cascading failures & evidence-based mitigations</sub>
    </td>
  </tr>
</table>

---

### 🔒 Security & Audit Ledger

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Decrypted Relational Security Audit Ledger.png" alt="Security Ledger" width="100%"/>
      <br/><sub><b>Decrypted Relational Security Audit Ledger</b></sub>
      <br/><sub>AES-256 decrypted telemetry rows with breach counts and crypto diagnostics JSON</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Core Infrastructure Features Manifest Matrix.png" alt="Feature Matrix" width="100%"/>
      <br/><sub><b>Core Infrastructure Features Manifest Matrix</b></sub>
      <br/><sub>Zero-trust privacy grid — cipher engine status and security indices</sub>
    </td>
  </tr>
</table>

---

### 📚 Learning Guide

<table>
  <tr>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Getting Started - Platform Deployment Checklist.png" alt="Getting Started" width="100%"/>
      <br/><sub><b>Getting Started Checklist</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Platform Learning Guide Dropdown Select.png" alt="Learning Guide" width="100%"/>
      <br/><sub><b>Interactive Learning Guide</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Deep Dive Learning Module - Multi-Agent AI Fusion Core.png" alt="AI Fusion Module" width="100%"/>
      <br/><sub><b>AI Fusion Core Deep Dive</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Deep Dive Learning Module - Acoustic Anomaly Engine.png" alt="Acoustic Module" width="100%"/>
      <br/><sub><b>Acoustic Anomaly Engine</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Deep Dive Learning Module - Cryptographic Architecture Vault.png" alt="Crypto Module" width="100%"/>
      <br/><sub><b>Cryptographic Architecture Vault</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Deep Dive Learning Module - Geographic Smart-City Mappings.png" alt="Geo Module" width="100%"/>
      <br/><sub><b>Geographic Smart-City Mappings</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Deep Dive Learning Module - State Machine Deep Dive.png" alt="State Machine" width="100%"/>
      <br/><sub><b>State Machine Deep Dive</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Learning Module - Predictive ARIMA Optimization.png" alt="ARIMA" width="100%"/>
      <br/><sub><b>Predictive ARIMA Optimization</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Learning Module - Sandbox Analyzer.png" alt="Sandbox Module" width="100%"/>
      <br/><sub><b>Sandbox Analyzer Module</b></sub>
    </td>
  </tr>
</table>

---

## ⚙️ Technology Stack

<table>
  <tr>
    <th>Layer</th>
    <th>Technology</th>
    <th>Purpose</th>
    <th>Version</th>
  </tr>
  <tr>
    <td>🌐 <b>Backend API</b></td>
    <td>FastAPI + Uvicorn</td>
    <td>REST microservice, JWT middleware, RBAC enforcement</td>
    <td>≥ 0.110</td>
  </tr>
  <tr>
    <td>🖥️ <b>Frontend</b></td>
    <td>Streamlit</td>
    <td>8-tab production dashboard with cyberpunk design system</td>
    <td>≥ 1.31</td>
  </tr>
  <tr>
    <td>👁️ <b>Computer Vision</b></td>
    <td>YOLOv8 (Ultralytics)</td>
    <td>Real-time COCO vehicle detection & camera tamper detection</td>
    <td>≥ 8.0</td>
  </tr>
  <tr>
    <td>🤖 <b>NLP / LLM</b></td>
    <td>DistilBERT + Qwen 2.5</td>
    <td>Zero-shot classification + conversational copilot</td>
    <td>HF Transformers ≥ 4.38</td>
  </tr>
  <tr>
    <td>🔥 <b>Deep Learning</b></td>
    <td>PyTorch</td>
    <td>Inference runtime for all neural models</td>
    <td>≥ 2.2</td>
  </tr>
  <tr>
    <td>📊 <b>Visualisation</b></td>
    <td>Plotly + pandas</td>
    <td>Interactive charts, Mapbox globe, heatmaps</td>
    <td>≥ 6.7 / ≥ 2.2</td>
  </tr>
  <tr>
    <td>🗄️ <b>Database</b></td>
    <td>SQLite + SQLAlchemy</td>
    <td>Relational ledger with AES-256 encrypted payloads</td>
    <td>≥ 2.0</td>
  </tr>
  <tr>
    <td>🔐 <b>Security</b></td>
    <td>cryptography (Fernet)</td>
    <td>AES-256-CBC + HMAC-SHA256 symmetric vault</td>
    <td>≥ 42.0</td>
  </tr>
  <tr>
    <td>📡 <b>Geocoding</b></td>
    <td>OpenStreetMap Nominatim</td>
    <td>Global lat/lon resolution with simulated offline fallback</td>
    <td>REST API</td>
  </tr>
  <tr>
    <td>🧪 <b>Testing</b></td>
    <td>pytest + FastAPI TestClient</td>
    <td>6-test automated suite covering all security & AI layers</td>
    <td>≥ 9.0</td>
  </tr>
</table>

---

## 🚀 Quick Start Guide

### Prerequisites

```bash
Python >= 3.11
pip >= 23.0
Git
```

### 1. Clone the Repository

```bash
git clone https://github.com/shambhushekharsinha-engg/AEGIS-Traffic.git
cd AEGIS-Traffic
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** YOLOv8 (`yolov8n.pt`) and HuggingFace models download automatically on first boot.

### 3. Start the FastAPI Backend

```bash
uvicorn app.main:app --reload --port 8000
```

> Backend boots at **http://127.0.0.1:8000** · Swagger UI at **http://127.0.0.1:8000/docs**

### 4. Launch the Streamlit Dashboard

```bash
# In a separate terminal
streamlit run dashboard/app.py
```

> Dashboard available at **http://localhost:8501**

### 5. Login with Demo Credentials

| Username | Password | Clearance |
|---|---|---|
| `admin` | `admin123` | 🔴 Admin — Full access, ledger, exports |
| `operator` | `operator123` | 🟢 Operator — Scan & copilot |
| `auditor` | `auditor123` | 🟡 Auditor — Ledger read + exports |

---

## 🔐 Security Architecture

```
┌──────────────────────────────────────────────────────────┐
│              ZERO-TRUST SECURITY LAYERS                  │
├──────────────────────────────────────────────────────────┤
│  Layer 1 — Password Hashing                              │
│  PBKDF2-HMAC-SHA256 · 100,000 iterations · 16-byte salt │
│  secrets.compare_digest() constant-time verification     │
├──────────────────────────────────────────────────────────┤
│  Layer 2 — Session Tokens                                │
│  Custom HMAC-SHA256 JWT · 1-hour TTL · Bearer scheme     │
│  Every protected FastAPI route: Depends(get_current_user)│
├──────────────────────────────────────────────────────────┤
│  Layer 3 — Role-Based Access Control (RBAC)              │
│  Admin → Full access (ledger, exports, all endpoints)    │
│  Operator → Analyze + chat only                          │
│  Auditor  → Ledger read + exports                        │
│  Unauth   → 401 on all protected routes                  │
├──────────────────────────────────────────────────────────┤
│  Layer 4 — Database Encryption                           │
│  Fernet (AES-128-CBC + HMAC-SHA256) per-row encryption   │
│  Raw SQLite binary inspection = unreadable ciphertext    │
├──────────────────────────────────────────────────────────┤
│  Layer 5 — AI Prompt Injection Firewall                  │
│  6-category keyword blocklist on /api/v1/chat            │
│  "system prompt" · "reveal key" · "bypass" blocked       │
└──────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Fusion Pipeline

The **Multimodal Fusion Core** combines three independent intelligence layers:

```
Visual Stream  ──▶  YOLOv8 Detection  ──▶  Vehicle Count + Confidence
                                             Camera Tamper Flag
                                                    │
                                                    ▼
Acoustic Stream ──▶  FFT Analysis   ──▶  dB SPL + Peak Frequency
                                          Siren / Collision / Ambient
                                                    │
                                                    ▼
                    ┌──────────────────────────────────────────┐
                    │      FUSION CONTEXT STRING               │
                    │  "Vehicles: 12. Siren detected 920Hz    │
                    │   at 84dB. Scenario: emergency."         │
                    └──────────────────────────────────────────┘
                                                    │
                                                    ▼
                    DistilBERT MNLI Zero-Shot ──▶  Classification
                    Labels: [normal, congested,
                             accident, emergency]
                                                    │
                                                    ▼
                    ┌──────────────────────────────────────────┐
                    │       HEURISTIC OVERRIDE MATRIX          │
                    │  Siren + >80dB → EMERGENCY (PRIORITY 1) │
                    │  Collision + >85dB → ALL RED (P2)        │
                    │  Count ≥9 → CONGESTION (P3)              │
                    │  Camera Blocked → FLASHING YELLOW        │
                    └──────────────────────────────────────────┘
                                                    │
                                                    ▼
                    Signal Phase · Timing · Advisory · Alert Status
```

---

## ⚙️ Operating Modes

| Mode | Icon | Behaviour | Signal State |
|---|---|---|---|
| **AI Automated Fusion** | 🤖 | YOLOv8 + DistilBERT real-time inference | Adaptive (15s / 30s / 45s / 25s) |
| **Manual Override** | 🎛️ | Operator sets phase & timer directly | Custom (5–60s, any phase) |
| **Security Lockdown** | 🔒 | All inputs suspended, ledger isolated | ALL RED — 0s green |
| **Predictive Optimization** | 🔮 | ARIMA demand simulation, proactive green | Extended 40s North-South |

---

## 📂 Project Structure

```
Aegis-MHR/
│
├── app/                          # FastAPI backend microservice
│   ├── main.py                   # REST API, JWT auth, routes
│   ├── core/
│   │   ├── vision_module.py      # YOLOv8 synthetic frame analyzer
│   │   └── audio_module.py       # FFT acoustic anomaly detector
│   ├── pipeline/
│   │   ├── fusion_core.py        # Multimodal decision engine
│   │   ├── history_logger.py     # AES-256 encrypted SQLite vault
│   │   └── simulate_pipeline.py  # Offline simulation pipeline
│   └── tests/
│       └── test_traffic.py       # 6-test automated pytest suite
│
├── dashboard/
│   └── app.py                    # Streamlit production dashboard (8 tabs)
│
├── data/
│   ├── audio_samples/            # WAV files for acoustic testing
│   └── aegis_secure_vault.db     # AES-256 encrypted SQLite ledger
│
├── Project Demo/
│   └── screenshots/              # 25 live platform screenshots
│
├── yolov8n.pt                    # Pre-trained YOLOv8-Nano weights
├── requirements.txt              # Python dependency manifest
├── .env                          # Secret key vault (auto-generated)
└── README.md                     # This file
```

---

## 🧪 Test Suite

The automated test suite covers all critical system layers:

```bash
python -m pytest app/tests/test_traffic.py -v
```

```
app/tests/test_traffic.py::test_vision_engine_synthetic_rendering  PASSED  ✅
app/tests/test_traffic.py::test_audio_engine_siren_detection        PASSED  ✅
app/tests/test_traffic.py::test_multimodal_fusion_priority_rules    PASSED  ✅
app/tests/test_traffic.py::test_fastapi_endpoints_clearance         PASSED  ✅
app/tests/test_traffic.py::test_jwt_auth_flow                       PASSED  ✅
app/tests/test_traffic.py::test_operational_modes                   PASSED  ✅
═══════════════════════════════════════════════════════════
6 passed · 0 failed · 35s
```

| Test | What It Verifies |
|---|---|
| `test_vision_engine_synthetic_rendering` | YOLOv8 frame synthesis, car detection, base64 image output |
| `test_audio_engine_siren_detection` | FFT siren vs ambient classification, dB level measurement |
| `test_multimodal_fusion_priority_rules` | Normal / Emergency / Collision priority ladder logic |
| `test_fastapi_endpoints_clearance` | 401 unauthenticated, 403 operator on ledger, 200 admin |
| `test_jwt_auth_flow` | Register → Login → JWT → Analyze → 403 ledger gate |
| `test_operational_modes` | Lockdown ALL RED, Manual Override phase, Predictive 40s |

---

## 🌍 Geographic Registry

AEGIS-Traffic can initialize **any intersection on Earth** as an active node:

```
Sidebar → Type any location → Click "📡 Initialize Site Node"
```

**Supported examples:**
- `Times Square, New York`
- `Shibuya Crossing, Tokyo`
- `Arc de Triomphe, Paris`
- `Sheikh Zayed Road, Dubai`
- `Trafalgar Square, London`
- `Connaught Place, New Delhi`
- Any GPS coordinates or address worldwide

Uses **OpenStreetMap Nominatim** for geocoding with a deterministic hash-based fallback if the geocoder is rate-limited.

---

## 🤖 AI Copilot Assistant

The **AEGIS Copilot** is a context-aware AI chatbot powered by **Qwen 2.5** with:

- 🛡️ **Prompt injection firewall** blocking 6 attack categories
- 🎯 **Active scan context injection** — answers based on the current live scene
- ⚡ **Quick-prompt buttons** for common traffic queries
- 💬 **Persistent session history** within the browser session

**Example queries:**
```
"What should I do about the current congestion?"
"Explain the emergency vehicle priority override."
"How does camera tamper detection work?"
"What is the optimal signal timing strategy for rush hour?"
```

---

## 📈 Analytics & Dataset Analyzer

### Live Ledger Analytics *(Admin / Auditor only)*
- Hazard Index time-series area chart
- Vehicle volume bar chart by scenario
- Latency vs vehicle load scatter plot
- Operational mode donut distribution
- Scenario frequency bar chart
- Signal timing histogram
- Hazard-by-scenario box plot
- One-click CSV export of decrypted ledger

### Dataset File Analyzer *(All roles)*
Upload any traffic dataset for instant analysis:

```
Supported Formats: CSV · Excel (.xlsx/.xls) · JSON
```

**Features:**
- Auto column type detection (`timestamp`, `volume`, `speed`, `vehicles`)
- 7 configurable chart types: Line · Bar · Scatter · Pie · Box · Heatmap · Histogram
- Schema profiler: dtype table + null counts + numeric describe stats
- **AI-powered insights** — Qwen 2.5 generates 5 actionable recommendations
- Download processed CSV

**Recommended public datasets:**
| Source | URL |
|---|---|
| UK Dept for Transport | data.gov.uk |
| Kaggle Traffic Flow | kaggle.com/datasets/fedesoriano/traffic-flow-forecasting |
| Chicago Crash Data | data.cityofchicago.org |
| TfL London | data.london.gov.uk |
| SUMO Simulation | zenodo.org/record/7008567 |

---

## 📖 API Reference

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/login` | None | Any | Login → returns JWT |
| `POST` | `/api/v1/auth/register` | None | Any | Register new operator |
| `POST` | `/api/v1/analyze` | Bearer JWT | All | Run multimodal scenario scan |
| `GET` | `/api/v1/history` | Bearer JWT | Admin/Auditor | Pull decrypted ledger |
| `POST` | `/api/v1/chat` | Bearer JWT | All | AI copilot message |
| `GET` | `/` | None | Any | Health check |

### Example Request — Analyze Endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "emergency",
    "vision_threshold": 0.4,
    "model_tier": "YOLOv8-Nano (Speed Edge)",
    "location_name": "Times Square, New York",
    "latitude": 40.7580,
    "longitude": -73.9855,
    "operational_mode": "AI Automated Fusion"
  }'
```

### Example Response

```json
{
  "risk_score": 88,
  "latency_ms": 142.5,
  "fusion_layer": {
    "alert_status": "🚨 EMERGENCY OVERRIDE (PRIORITY 1)",
    "active_phase": "EMERGENCY VEHICLE PRIORITY (GREEN)",
    "signal_timing_seconds": 25,
    "vehicle_count": 6,
    "rerouting_advisory": "Emergency vehicle approaching. Clear North-South corridor immediately.",
    "automated_incident_report": "PRIORITY 1 — Siren detected at 920Hz / 84dB..."
  },
  "telemetry": { ... },
  "system_telemetry_metrics": { ... }
}
```

---

## 🛠️ Configuration & Environment

AEGIS-Traffic auto-generates a `.env` file on first boot:

```env
# Auto-generated by AEGIS-Traffic on first boot
AEGIS_SECRET_KEY=<Fernet-compatible base64 key>
```

| Variable | Description | Default |
|---|---|---|
| `AEGIS_SECRET_KEY` | Fernet AES-256 DB encryption key | Auto-generated 32-byte URL-safe base64 |
| `PORT` | Uvicorn bind port | `8000` |

> ⚠️ **Security Note:** Never commit `.env` to version control. It is already listed in `.gitignore`.

---

## 📜 License

**MIT License — © 2026 [AEGIS-Traffic](https://aegis-traffic.vercel.app)**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer Profile

<div align="center">

<br/>

<table>
  <tr>
    <td align="center" width="100%">
      <img src="https://img.shields.io/badge/Developer-Shambhu%20Shekhar%20Sinha-00f0ff?style=for-the-badge&labelColor=010308" />
      <br/><br/>
      <table>
        <tr>
          <td>👤 <b>Name</b></td>
          <td>Shambhu Shekhar Sinha</td>
        </tr>
        <tr>
          <td>🎓 <b>Degree</b></td>
          <td>B.Tech — Computer Science & Engineering (AI & ML)</td>
        </tr>
        <tr>
          <td>🏫 <b>College</b></td>
          <td>Greater Noida Institute of Technology</td>
        </tr>
        <tr>
          <td>🏛️ <b>University</b></td>
          <td>Dr. APJ Abdul Kalam Technological University, Lucknow</td>
        </tr>
        <tr>
          <td>📍 <b>Location</b></td>
          <td>Greater Noida, Uttar Pradesh, India</td>
        </tr>
        <tr>
          <td>🐙 <b>GitHub</b></td>
          <td><a href="https://github.com/shambhushekharsinha-engg">@shambhushekharsinha-engg</a></td>
        </tr>
        <tr>
          <td>🌐 <b>Deployment</b></td>
          <td><a href="https://aegis-traffic.vercel.app">aegis-traffic.vercel.app</a></td>
        </tr>
      </table>
    </td>
  </tr>
</table>

<br/>

<img src="https://img.shields.io/badge/B.Tech-CSE%20%7C%20AI%20%26%20ML-00f0ff?style=flat-square&labelColor=010308"/>
<img src="https://img.shields.io/badge/GNIT-Greater%20Noida-10b981?style=flat-square"/>
<img src="https://img.shields.io/badge/AKTU-Lucknow-FF4B4B?style=flat-square"/>
<img src="https://img.shields.io/badge/GitHub-shambhushekharsinha--engg-181717?style=flat-square&logo=github"/>

</div>

---

<div align="center">

**Built with ❤️ for Smart Cities · Powered by AI · Secured by Zero-Trust**

<br/>

<img src="https://img.shields.io/badge/YOLOv8-Computer%20Vision-purple?style=flat-square"/>
<img src="https://img.shields.io/badge/DistilBERT-Zero--Shot%20NLP-FFD21E?style=flat-square&logo=huggingface&logoColor=black"/>
<img src="https://img.shields.io/badge/Qwen%202.5-AI%20Copilot-00f0ff?style=flat-square"/>
<img src="https://img.shields.io/badge/AES--256-Encrypted%20Vault-10b981?style=flat-square"/>
<img src="https://img.shields.io/badge/FastAPI-REST%20Microservice-009688?style=flat-square&logo=fastapi"/>
<img src="https://img.shields.io/badge/Streamlit-Live%20Dashboard-FF4B4B?style=flat-square&logo=streamlit"/>

<br/><br/>

**⭐ Star this repo if AEGIS-Traffic helped your smart city research!**

</div>