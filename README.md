<div align="center">

<img src="https://img.shields.io/badge/AEGIS%20TRAFFIC-v7.0%20PRODUCTION-00f0ff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzAwZjBmZiIgZD0iTTEyIDJMMiA3bDEwIDUgMTAtNXoiLz48cGF0aCBmaWxsPSIjMDBmMGZmIiBkPSJNMiAxN2wxMCA1IDEwLTV2LTZMMTIgMTYgMiAxMXoiLz48L3N2Zz4=&labelColor=010308" />

# 🚦 AEGIS — Traffic
### **Adaptive Edge-Grade Intelligence System for Smart-City Traffic Management**

<br/>

> *An industrial-grade, production-deployed AI platform that fuses **Computer Vision (YOLOv8)**, **Acoustic Anomaly Detection (FFT)**, **Zero-Shot NLP (DistilBERT)**, **ANPR (Automatic Number Plate Recognition)**, and **Traffic Violation Detection** into a real-time multimodal decision engine — secured end-to-end with AES-256 encryption, JWT authentication, and role-based access control.*

<br/>

---

### 🌐 Live Deployments

| Platform | Link | Description |
|:---:|:---:|:---|
| 🖥️ **Frontend** | [![Streamlit](https://img.shields.io/badge/STREAMLIT%20DASHBOARD-Live%20Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white&labelColor=010308)](https://aegis-traffic.streamlit.app/) | Full 10-tab Streamlit dashboard — all original tabs + new features |
| ⚙️ **Backend API** | [![Vercel](https://img.shields.io/badge/FASTAPI%20BACKEND-aegis--traffic.vercel.app-00f0ff?style=for-the-badge&logo=vercel&logoColor=white&labelColor=010308)](https://aegis-traffic.vercel.app) | FastAPI REST microservice — all AI inference & data endpoints |
| 📖 **API Docs** | [![Swagger](https://img.shields.io/badge/SWAGGER%20UI-/docs-009688?style=for-the-badge&logo=swagger&logoColor=white&labelColor=010308)](https://aegis-traffic.vercel.app/docs) | Interactive Swagger / OpenAPI documentation |

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-purple?style=flat-square&logo=yolo&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyTorch-2.2+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black"/>
  <img src="https://img.shields.io/badge/SQLite-AES--256%20Encrypted-003B57?style=flat-square&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/JWT-HMAC--SHA256-black?style=flat-square&logo=jsonwebtokens&logoColor=white"/>
  <img src="https://img.shields.io/badge/Deployed-Vercel%20%2B%20Streamlit%20Cloud-00f0ff?style=flat-square"/>
  <img src="https://img.shields.io/badge/Tests-6%2F6%20PASSING-10b981?style=flat-square&logo=pytest&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-10b981?style=flat-square"/>
</p>

</div>

---

## 📋 Table of Contents

- [🏗️ Architecture Overview](#️-architecture-overview)
- [✨ Core Feature Matrix](#-core-feature-matrix)
- [🖥️ Frontend Screenshots](#️-frontend-screenshots)
- [⚙️ Backend Screenshots](#️-backend-screenshots)
- [🆕 New Features Added](#-new-features-added)
- [🛠️ Technology Stack](#️-technology-stack)
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
- [👨‍💻 Developer Profile](#-developer-profile)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           AEGIS-TRAFFIC  v7.0                                       │
│                      SMART CITY OPERATIONS PLATFORM                                 │
├──────────────────────────────────┬──────────────────────────────────────────────────┤
│   STREAMLIT FRONTEND             │          FASTAPI BACKEND (Vercel)                │
│   dashboard/app.py               │          app/main.py                             │
│   (Streamlit Community Cloud)    │                                                  │
│                                  │                                                  │
│  ┌──────────────────────────┐    │  ┌────────────────────────────────────────────┐  │
│  │  Zero-Trust Login Portal │────┼─▶│  JWT Auth + PBKDF2 Vault                  │  │
│  │  Operator Registration   │    │  │  POST /api/v1/auth/login                  │  │
│  └──────────────────────────┘    │  │  POST /api/v1/auth/register               │  │
│  ┌──────────────────────────┐    │  └────────────────────────────────────────────┘  │
│  │  📊 Operations HUD       │    │  ┌────────────────────────────────────────────┐  │
│  │  🚥 Signal Controller    │────┼─▶│  Multimodal Fusion Engine                 │  │
│  │  🔊 Acoustic Waveform    │    │  │  POST /api/v1/analyze                     │  │
│  └──────────────────────────┘    │  │  ┌──────────┐  ┌────────┐  ┌───────────┐ │  │
│  ┌──────────────────────────┐    │  │  │ YOLOv8   │  │  FFT   │  │DistilBERT │ │  │
│  │  📈 Analytics Suite      │────┼─▶│  │ Vision   │  │ Audio  │  │  NLP      │ │  │
│  │  🌍 Map Intelligence     │    │  │  └──────────┘  └────────┘  └───────────┘ │  │
│  └──────────────────────────┘    │  └────────────────────────────────────────────┘  │
│  ┌──────────────────────────┐    │  ┌────────────────────────────────────────────┐  │
│  │  🤖 AI Copilot Chat      │────┼─▶│  Qwen 2.5 LLM Guardrailed Chat           │  │
│  └──────────────────────────┘    │  │  POST /api/v1/chat                        │  │
│  ┌──────────────────────────┐    │  └────────────────────────────────────────────┘  │
│  │  🚘 ANPR & Violations    │────┼─▶│  GET /api/v1/anpr/{scenario}              │  │
│  │  ⚙️ Pipeline Status      │    │  │  GET /api/v1/violations/{scenario}        │  │
│  └──────────────────────────┘    │  │  GET /api/v1/pipeline/status              │  │
│  ┌──────────────────────────┐    │  └────────────────────────────────────────────┘  │
│  │  🔒 Security Ledger      │────┼─▶│  AES-256 Encrypted SQLite Vault           │  │
│  │  📂 Dataset Analyzer     │    │  │  GET /api/v1/history  (Admin/Auditor)     │  │
│  └──────────────────────────┘    │  └────────────────────────────────────────────┘  │
└──────────────────────────────────┴──────────────────────────────────────────────────┘
```

---

## ✨ Core Feature Matrix

| Category | Feature | Implementation |
|:---|:---|:---|
| 🤖 **AI Vision** | Real-time vehicle detection | YOLOv8-Nano COCO detection + synthetic frame synthesis |
| 🔊 **Acoustics** | Sound anomaly detection | RMS dB measurement + FFT frequency spectrum analysis |
| 🧠 **NLP Fusion** | Multimodal context classification | DistilBERT zero-shot MNLI (Hugging Face Transformers) |
| 💬 **AI Copilot** | Traffic advisory chatbot | Qwen 2.5-0.5B-Instruct + prompt-injection guardrails |
| 🚘 **ANPR** | Automatic plate recognition | Scenario-aware OCR simulation + flagging registry |
| ⚠️ **Violations** | Traffic violation detection | Fine calculation, violation typing, vehicle ledger |
| 📊 **Traffic Analytics** | Density · Queue · Speed · Lanes | Real-time KPIs from every multimodal scan |
| ⚙️ **Pipeline Status** | Module health matrix | Live status of all 6 AI/system modules |
| 🔒 **Auth** | Zero-trust authentication | JWT HMAC-SHA256 + PBKDF2-SHA256 (100k iterations) |
| 🛡️ **Encryption** | Database vault | Fernet AES-256-CBC + HMAC-SHA256 per-row encryption |
| 👥 **RBAC** | Role-based clearance | Admin / Operator / Auditor tier enforcement |
| 🌍 **Geo** | Global site initialization | Nominatim OSM geocoding + hash-based fallback |
| 🗺️ **Mapping** | Global incident registry | Plotly Mapbox dark-mode scatter globe |
| ⚙️ **Modes** | 4-state operating machine | AI Auto / Manual Override / Lockdown / Predictive |
| 📈 **Analytics** | Production telemetry suite | 7 Plotly chart types: area · bar · scatter · pie · box · histogram |
| 📂 **Data Upload** | Custom dataset analyzer | CSV / Excel / JSON + 7 chart types + AI insights |
| 🧪 **Sandbox** | Offline simulation sandbox | Custom sensor parameter testing + latency benchmarking |
| 🪝 **Webhooks** | First responder alert dispatch | HTTP POST to municipal traffic operations hubs |
| 📖 **Knowledge** | Diagnostic manual | 7 problem profiles with root causes & mitigations |
| 📚 **Learning** | Interactive learning guide | 9 deep-dive topics: ATSC · Fusion · ARIMA · Crypto · Geo |
| 📥 **Export** | Audit ledger download | Decrypted CSV export (Admin / Auditor clearance only) |

---

## 🖥️ Frontend Screenshots

> All screenshots captured from the live Streamlit dashboard at `dashboard/app.py`

### 🔐 Authentication Portal

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Zero-Trust Authentication Deck.png" alt="Zero-Trust Login" width="100%"/>
      <br/><sub><b>Zero-Trust Authentication Deck</b></sub>
      <br/><sub>JWT-secured login with role clearance badges and credential vault</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/User Registration Gateway.png" alt="User Registration" width="100%"/>
      <br/><sub><b>Operator Registration Gateway</b></sub>
      <br/><sub>Secure operator onboarding with PBKDF2-SHA256 password hashing</sub>
    </td>
  </tr>
</table>

---

### 📊 Operations HUD

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Initial Operations HUD State.png" alt="HUD Initial State" width="100%"/>
      <br/><sub><b>Initial Operations HUD — Sensor Grid Standby</b></sub>
      <br/><sub>Boot screen awaiting scenario scan — displays system status indicators</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Multimodal Telemetry Core Operations Cockpit.png" alt="Operations Cockpit" width="100%"/>
      <br/><sub><b>Multimodal Telemetry Core Operations Cockpit</b></sub>
      <br/><sub>Live YOLOv8 feed, signal controller, acoustic waveform & advisory</sub>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <img src="Project Demo/screenshots/Frontend/Adaptive Signal Controller & Real-Time Advisory Module.png" alt="Signal Controller" width="100%"/>
      <br/><sub><b>Adaptive Signal Controller & Real-Time Advisory Module</b></sub>
      <br/><sub>Phase-aware signal state machine with live rerouting advisories and acoustic telemetry</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/High-Risk Incident Ingest Matrix — Accident Collision Vector.png" alt="Accident Mode" width="100%"/>
      <br/><sub><b>High-Risk Incident Ingest — Accident Collision Vector</b></sub>
      <br/><sub>Priority 2 collision detection with ALL RED signal state and incident report</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Priority Vehicle Ingest Matrix — Emergency Inbound Mode.png" alt="Emergency Mode" width="100%"/>
      <br/><sub><b>Priority Vehicle Ingest — Emergency Inbound Mode</b></sub>
      <br/><sub>Emergency vehicle priority override — North-South green corridor cleared</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Sensor Integrity Ingest View — Tampered Feed Mitigation State.png" alt="Tamper Mode" width="100%"/>
      <br/><sub><b>Sensor Integrity Ingest — Tampered Feed Mitigation State</b></sub>
      <br/><sub>Camera tamper detection activates FLASHING YELLOW and security alert</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/End-to-End Computational Ingestion Data Flow.png" alt="Data Flow" width="100%"/>
      <br/><sub><b>End-to-End Computational Ingestion Data Flow</b></sub>
      <br/><sub>Raw detection payload, telemetry JSON and visual detection table</sub>
    </td>
  </tr>
</table>

---

### 📈 Analytics Suite

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Cryptographic Analytics Suite Upper Deck.png" alt="Analytics Upper Deck" width="100%"/>
      <br/><sub><b>Cryptographic Analytics Suite — Upper Deck</b></sub>
      <br/><sub>KPI tiles, Hazard Index time-series area chart & mode distribution pie</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Systemic Telemetry Analytics Lower Deck.png" alt="Analytics Lower Deck" width="100%"/>
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
      <img src="Project Demo/screenshots/Frontend/Geographic Smart-City Node Intelligence Grid.png" alt="Map Intelligence" width="80%"/>
      <br/><sub><b>Geographic Smart-City Node Intelligence Grid</b></sub>
      <br/><sub>Global incident registry on dark-mode Mapbox canvas with risk-score colour scaling</sub>
    </td>
  </tr>
</table>

---

### 🤖 AI Copilot

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Guardrailed AI Traffic Operations Copilot.png" alt="AI Copilot" width="100%"/>
      <br/><sub><b>Guardrailed AI Traffic Operations Copilot</b></sub>
      <br/><sub>Qwen 2.5 chatbot with 6-category prompt injection firewall</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Dynamic AI Chat History & Security Guardrails.png" alt="Chat History" width="100%"/>
      <br/><sub><b>Dynamic AI Chat History & Security Guardrails</b></sub>
      <br/><sub>Persistent session memory, quick-prompt buttons and role-aware responses</sub>
    </td>
  </tr>
</table>

---

### 🚘 ANPR & Traffic Violations *(New Feature)*

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/ANPR & Violation Analysis Target Ingestion Dropdown.png" alt="ANPR Dropdown" width="100%"/>
      <br/><sub><b>ANPR & Violation Analysis — Target Ingestion Dropdown</b></sub>
      <br/><sub>Scenario-based ANPR scan selector with violation analysis trigger</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/ANPR Registry & Violation Status Deck — Baseline Mode.png" alt="ANPR Baseline" width="100%"/>
      <br/><sub><b>ANPR Registry & Violation Status Deck — Baseline Mode</b></sub>
      <br/><sub>Plate registry with flagged/clear status and violation fine ledger</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Automated Violation Ingestion Bridge — Congested Traffic Vector.png" alt="Violation Congested" width="100%"/>
      <br/><sub><b>Automated Violation Ingestion — Congested Traffic Vector</b></sub>
      <br/><sub>Congestion-triggered violations with fine amounts and vehicle IDs</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Microservice Infrastructure Module Health Matrix.png" alt="Pipeline Status" width="100%"/>
      <br/><sub><b>Microservice Infrastructure — Module Health Matrix</b></sub>
      <br/><sub>Live pipeline status showing all AI module health across the system</sub>
    </td>
  </tr>
</table>

---

### 🧪 Sandbox & Simulation

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Multimodal Telemetry Simulation Sandbox.png" alt="Sandbox" width="100%"/>
      <br/><sub><b>Multimodal Telemetry Simulation Sandbox</b></sub>
      <br/><sub>Custom scenario testing, iteration benchmarking and latency profiling</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Operational Diagnostics & Mitigation Manual.png" alt="Diagnostics" width="100%"/>
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
      <img src="Project Demo/screenshots/Frontend/Decrypted Relational Security Audit Ledger.png" alt="Security Ledger" width="100%"/>
      <br/><sub><b>Decrypted Relational Security Audit Ledger</b></sub>
      <br/><sub>AES-256 decrypted telemetry rows with breach counts and crypto diagnostics JSON</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Frontend/Core Infrastructure Features Manifest Matrix.png" alt="Feature Matrix" width="100%"/>
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
      <img src="Project Demo/screenshots/Frontend/Getting Started - Platform Deployment Checklist.png" alt="Getting Started" width="100%"/>
      <br/><sub><b>Getting Started — Platform Deployment Checklist</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Platform Learning Guide Dropdown Select.png" alt="Learning Guide" width="100%"/>
      <br/><sub><b>Interactive Learning Guide — Topic Selector</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Deep Dive Learning Module - Multi-Agent AI Fusion Core.png" alt="AI Fusion Module" width="100%"/>
      <br/><sub><b>Deep Dive — Multi-Agent AI Fusion Core</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Deep Dive Learning Module - Acoustic Anomaly Engine.png" alt="Acoustic Module" width="100%"/>
      <br/><sub><b>Deep Dive — Acoustic Anomaly Engine</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Deep Dive Learning Module - Cryptographic Architecture Vault.png" alt="Crypto Module" width="100%"/>
      <br/><sub><b>Deep Dive — Cryptographic Architecture Vault</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Deep Dive Learning Module - Geographic Smart-City Mappings.png" alt="Geo Module" width="100%"/>
      <br/><sub><b>Deep Dive — Geographic Smart-City Mappings</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Deep Dive Learning Module - State Machine Deep Dive.png" alt="State Machine" width="100%"/>
      <br/><sub><b>Deep Dive — 4-Mode State Machine</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Learning Module - Predictive ARIMA Optimization.png" alt="ARIMA" width="100%"/>
      <br/><sub><b>Learning — Predictive ARIMA Optimization</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Learning Module - Sandbox Analyzer.png" alt="Sandbox Module" width="100%"/>
      <br/><sub><b>Learning — Sandbox Analyzer Module</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Learning Module - Adaptive Signal Control (ATSC).png" alt="ATSC Module" width="100%"/>
      <br/><sub><b>Learning — Adaptive Signal Control (ATSC)</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Learning Module - Analytics & Production Telemetry.png" alt="Analytics Module" width="100%"/>
      <br/><sub><b>Learning — Analytics & Production Telemetry</b></sub>
    </td>
    <td align="center" width="33%">
      <img src="Project Demo/screenshots/Frontend/Guardrailed AI Traffic Operations Copilot.png" alt="Copilot Module" width="100%"/>
      <br/><sub><b>Guardrailed AI Copilot — Full Chat View</b></sub>
    </td>
  </tr>
</table>

---

## ⚙️ Backend Screenshots

> All screenshots captured from the FastAPI backend hosted on Vercel

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Smart City Core Authorization Interface.png" alt="Backend Auth" width="100%"/>
      <br/><sub><b>Smart City Core — Authorization Interface</b></sub>
      <br/><sub>FastAPI root dashboard — JWT-secured entry point and API status</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Systemic Flow Engine State — Nominal Control Active.png" alt="Nominal Control" width="100%"/>
      <br/><sub><b>Systemic Flow Engine State — Nominal Control Active</b></sub>
      <br/><sub>Normal traffic scenario API response with fusion layer output</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Multimodal Core Operations HUD — Ingestion Inits.png" alt="Backend HUD" width="100%"/>
      <br/><sub><b>Multimodal Core Operations HUD — Ingestion Initialisation</b></sub>
      <br/><sub>Backend analysis endpoint processing multimodal telemetry scan</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Operational Mode Routing Layer Select.png" alt="Mode Routing" width="100%"/>
      <br/><sub><b>Operational Mode Routing Layer Select</b></sub>
      <br/><sub>Mode-switching API logic — AI Fusion / Manual / Lockdown / Predictive</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Signal Preemption HUD — Emergency Vehicle Mode.png" alt="Emergency Backend" width="100%"/>
      <br/><sub><b>Signal Preemption HUD — Emergency Vehicle Mode</b></sub>
      <br/><sub>Priority 1 emergency override — API response with signal preemption data</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Incident Containment Active HUD — Collision Event Mode.png" alt="Collision Backend" width="100%"/>
      <br/><sub><b>Incident Containment HUD — Collision Event Mode</b></sub>
      <br/><sub>Priority 2 collision detection — ALL RED signal state API response</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Hardware Exception HUD — Camera Feed Tamper Mode.png" alt="Tamper Backend" width="100%"/>
      <br/><sub><b>Hardware Exception HUD — Camera Feed Tamper Mode</b></sub>
      <br/><sub>Sensor tamper detection API — FLASHING YELLOW state with security alert</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Adaptive Optimization Inits — Congested Queue Vector.png" alt="Congestion Backend" width="100%"/>
      <br/><sub><b>Adaptive Optimization — Congested Queue Vector</b></sub>
      <br/><sub>Congestion scenario with extended signal timing and rerouting advisory</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Localized Telemetry Lower Fold — Tactical AI Interface.png" alt="Telemetry Lower" width="100%"/>
      <br/><sub><b>Localized Telemetry Lower Fold — Tactical AI Interface</b></sub>
      <br/><sub>Acoustic profile, FFT spectrum and visual detection data in API response</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Sensor Integrity Matrix Lower Fold — Deep Learning Validation.png" alt="Sensor Integrity" width="100%"/>
      <br/><sub><b>Sensor Integrity Matrix Lower Fold — Deep Learning Validation</b></sub>
      <br/><sub>YOLOv8 detection confidence scores and acoustic anomaly classification</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Traffic Enforcement Lower Fold — Active Violation Ledger.png" alt="Violation Backend" width="100%"/>
      <br/><sub><b>Traffic Enforcement Lower Fold — Active Violation Ledger</b></sub>
      <br/><sub>Violation detection API response with fine amounts and vehicle identifiers</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/screenshots/Backend/Traffic Ingestion Lower Fold — Lane Enforcement Registry.png" alt="Lane Registry" width="100%"/>
      <br/><sub><b>Traffic Ingestion Lower Fold — Lane Enforcement Registry</b></sub>
      <br/><sub>ANPR plate registry API response with flagging status per vehicle</sub>
    </td>
  </tr>
</table>

---

## 🆕 New Features Added

The following features were newly engineered and integrated into AEGIS-Traffic:

| # | Feature | Endpoint | Description |
|:---:|:---|:---|:---|
| 1 | 🚘 **ANPR — Plate Recognition** | `GET /api/v1/anpr/{scenario}` | Automatic Number Plate Recognition with flagged/clear registry per scenario |
| 2 | ⚠️ **Traffic Violation Detection** | `GET /api/v1/violations/{scenario}` | Detects violations (red-light, speeding, no-stop), calculates fines, identifies vehicle IDs |
| 3 | 📊 **Traffic Analytics Engine** | Embedded in `/api/v1/analyze` | Returns density %, queue length (m), avg speed (km/h), density level label & per-lane counts |
| 4 | ⚙️ **Pipeline Status Dashboard** | `GET /api/v1/pipeline/status` | Real-time health matrix for all AI/system modules with stage-by-stage pipeline flow |
| 5 | 🖥️ **10-Tab Streamlit Dashboard** | `dashboard/app.py` | Original 8 tabs fully preserved + 2 new tabs: ANPR & Violations, Pipeline Status |
| 6 | 🌐 **Vercel-Safe ML Imports** | `app/main.py` | `try/except ImportError` guards on all heavy ML libs so Vercel boots cleanly without torch/transformers |

---

## 🛠️ Technology Stack

<table>
  <tr>
    <th>Layer</th>
    <th>Technology</th>
    <th>Purpose</th>
    <th>Version</th>
  </tr>
  <tr>
    <td>⚙️ <b>Backend API</b></td>
    <td>FastAPI + Uvicorn</td>
    <td>REST microservice, JWT middleware, RBAC enforcement, Vercel deployment</td>
    <td>≥ 0.110</td>
  </tr>
  <tr>
    <td>🖥️ <b>Frontend</b></td>
    <td>Streamlit</td>
    <td>10-tab production dashboard with cyberpunk design system</td>
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
    <td>Zero-shot classification + conversational AI copilot</td>
    <td>HF Transformers ≥ 4.38</td>
  </tr>
  <tr>
    <td>🔥 <b>Deep Learning</b></td>
    <td>PyTorch + torchaudio</td>
    <td>Inference runtime for all neural models + audio processing</td>
    <td>≥ 2.2</td>
  </tr>
  <tr>
    <td>📊 <b>Visualisation</b></td>
    <td>Plotly + pandas</td>
    <td>Interactive charts, Mapbox globe, heatmaps, canvas waveforms</td>
    <td>≥ 6.7 / ≥ 2.2</td>
  </tr>
  <tr>
    <td>🗄️ <b>Database</b></td>
    <td>SQLite + SQLAlchemy</td>
    <td>Relational audit ledger with AES-256 encrypted payloads</td>
    <td>≥ 2.0</td>
  </tr>
  <tr>
    <td>🔐 <b>Security</b></td>
    <td>cryptography (Fernet)</td>
    <td>AES-256-CBC + HMAC-SHA256 symmetric database vault</td>
    <td>≥ 42.0</td>
  </tr>
  <tr>
    <td>📡 <b>Geocoding</b></td>
    <td>OpenStreetMap Nominatim</td>
    <td>Global lat/lon resolution with hash-based offline fallback</td>
    <td>REST API</td>
  </tr>
  <tr>
    <td>🧪 <b>Testing</b></td>
    <td>pytest + FastAPI TestClient</td>
    <td>6-test automated suite covering all security & AI layers</td>
    <td>≥ 9.0</td>
  </tr>
  <tr>
    <td>🚀 <b>Deployment</b></td>
    <td>Vercel + Streamlit Cloud</td>
    <td>Backend on Vercel (serverless), Frontend on Streamlit Community Cloud</td>
    <td>Production</td>
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
|:---|:---|:---|
| `admin` | `admin123` | 🔴 Admin — Full access, ledger, exports, all endpoints |
| `operator` | `operator123` | 🟢 Operator — Scan, ANPR, copilot, sandbox |
| `auditor` | `auditor123` | 🟡 Auditor — Ledger read + CSV exports |

---

## 🔐 Security Architecture

```
┌──────────────────────────────────────────────────────────┐
│              ZERO-TRUST SECURITY LAYERS                  │
├──────────────────────────────────────────────────────────┤
│  Layer 1 — Password Hashing                              │
│  PBKDF2-HMAC-SHA256 · 100,000 iterations · 16-byte salt  │
│  secrets.compare_digest() constant-time verification      │
├──────────────────────────────────────────────────────────┤
│  Layer 2 — Session Tokens                                │
│  Custom HMAC-SHA256 JWT · 1-hour TTL · Bearer scheme      │
│  Every protected FastAPI route: Depends(get_current_user) │
├──────────────────────────────────────────────────────────┤
│  Layer 3 — Role-Based Access Control (RBAC)              │
│  Admin   → Full access (ledger, exports, all endpoints)  │
│  Operator → Analyze + chat + ANPR + violations           │
│  Auditor  → Ledger read + exports only                   │
│  Unauth   → HTTP 401 on all protected routes             │
├──────────────────────────────────────────────────────────┤
│  Layer 4 — Database Encryption                           │
│  Fernet (AES-128-CBC + HMAC-SHA256) per-row encryption   │
│  Raw SQLite binary inspection = unreadable ciphertext    │
├──────────────────────────────────────────────────────────┤
│  Layer 5 — AI Prompt Injection Firewall                  │
│  6-category keyword blocklist on /api/v1/chat            │
│  "system prompt" · "reveal key" · "bypass" all blocked   │
└──────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Fusion Pipeline

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
                                      ┌─────────────┼─────────────┐
                                      ▼             ▼             ▼
                              Signal Phase    ANPR Scan    Violation
                              Timing·Advisory  Plates·Flags  Detection·Fines
```

---

## ⚙️ Operating Modes

| Mode | Icon | Behaviour | Signal State |
|:---|:---:|:---|:---|
| **AI Automated Fusion** | 🤖 | YOLOv8 + DistilBERT real-time inference | Adaptive (15s / 30s / 45s / 25s) |
| **Manual Override** | 🎛️ | Operator sets phase & timer directly | Custom (5–90s, any phase) |
| **Security Lockdown** | 🔒 | All inputs suspended, ledger isolated | ALL RED — 0s green |
| **Predictive Optimization** | 🔮 | ARIMA demand simulation, proactive green | Extended 40s North-South |

---

## 📂 Project Structure

```
AEGIS-Traffic/
│
├── app/                             # FastAPI backend microservice
│   ├── main.py                      # REST API, JWT auth, all routes (Vercel entry)
│   ├── core/
│   │   ├── vision_module.py         # YOLOv8 synthetic frame analyzer
│   │   └── audio_module.py          # FFT acoustic anomaly detector
│   ├── pipeline/
│   │   ├── fusion_core.py           # Multimodal decision engine (DistilBERT)
│   │   ├── history_logger.py        # AES-256 encrypted SQLite audit vault
│   │   └── simulate_pipeline.py     # Offline simulation pipeline
│   └── tests/
│       └── test_traffic.py          # 6-test automated pytest suite
│
├── dashboard/
│   ├── app.py                       # Streamlit production dashboard (10 tabs)
│   └── requirements.txt             # Streamlit Cloud dependency manifest
│
├── data/
│   ├── audio_samples/               # WAV files for acoustic testing
│   └── aegis_secure_vault.db        # AES-256 encrypted SQLite ledger
│
├── Project Demo/
│   └── screenshots/
│       ├── Frontend/                # 33 live Streamlit dashboard screenshots
│       └── Backend/                 # 12 live FastAPI backend screenshots
│
├── yolov8n.pt                       # Pre-trained YOLOv8-Nano weights
├── requirements.txt                 # Backend Python dependency manifest
├── vercel.json                      # Vercel serverless deployment config
├── .python-version                  # Python version pin for Vercel
├── .env                             # Secret key vault (auto-generated)
└── README.md                        # This file
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
6 passed · 0 failed · ~30s
```

| Test | What It Verifies |
|:---|:---|
| `test_vision_engine_synthetic_rendering` | YOLOv8 frame synthesis, car detection, base64 image output |
| `test_audio_engine_siren_detection` | FFT siren vs ambient classification, dB level measurement |
| `test_multimodal_fusion_priority_rules` | Normal / Emergency / Collision priority ladder logic |
| `test_fastapi_endpoints_clearance` | 401 unauthenticated, 403 operator on ledger, 200 admin |
| `test_jwt_auth_flow` | Register → Login → JWT → Analyze → 403 ledger gate |
| `test_operational_modes` | Lockdown ALL RED, Manual Override phase, Predictive 40s |

---

## 🌍 Geographic Registry

AEGIS-Traffic can initialize **any intersection on Earth** as an active smart-city node:

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

Uses **OpenStreetMap Nominatim** for geocoding with a deterministic hash-based fallback if rate-limited.

---

## 🤖 AI Copilot Assistant

The **AEGIS Copilot** is a context-aware AI chatbot powered by **Qwen 2.5-0.5B-Instruct** with:

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
- Vehicle volume bar chart per scenario
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

---

## 📖 API Reference

| Method | Endpoint | Auth | Role | Description |
|:---:|:---|:---:|:---:|:---|
| `POST` | `/api/v1/auth/login` | None | Any | Login → returns JWT access token |
| `POST` | `/api/v1/auth/register` | None | Any | Register new operator account |
| `POST` | `/api/v1/analyze` | Bearer JWT | All | Run full multimodal scenario scan |
| `GET` | `/api/v1/history` | Bearer JWT | Admin/Auditor | Pull decrypted audit ledger |
| `POST` | `/api/v1/chat` | Bearer JWT | All | AI Copilot message exchange |
| `GET` | `/api/v1/anpr/{scenario}` | Bearer JWT | All | ANPR plate registry for scenario |
| `GET` | `/api/v1/violations/{scenario}` | Bearer JWT | All | Traffic violation detection |
| `GET` | `/api/v1/pipeline/status` | None | Any | Full pipeline module health matrix |
| `GET` | `/docs` | None | Any | Swagger UI interactive documentation |

### Example — Analyze Endpoint

```bash
curl -X POST https://aegis-traffic.vercel.app/api/v1/analyze \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "emergency",
    "operational_mode": "AI Automated Fusion",
    "location_name": "Times Square, New York",
    "latitude": 40.7580,
    "longitude": -73.9855
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
    "rerouting_advisory": "Emergency vehicle approaching. Clear North-South corridor immediately."
  },
  "traffic_analytics": {
    "traffic_density_percent": 45.2,
    "queue_length_meters": 87.5,
    "avg_speed_kmh": 28.3,
    "density_level": "MODERATE",
    "lane_counts": { "North": 2, "South": 2, "East": 1, "West": 1 }
  },
  "telemetry": { "..." : "..." },
  "system_telemetry_metrics": { "..." : "..." }
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
|:---|:---|:---|
| `AEGIS_SECRET_KEY` | Fernet AES-256 DB encryption key | Auto-generated 32-byte URL-safe base64 |
| `AEGIS_BACKEND_URL` | Streamlit → backend URL override | `http://127.0.0.1:8000` |
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

<img src="https://img.shields.io/badge/Developer-Shambhu%20Shekhar%20Sinha-00f0ff?style=for-the-badge&labelColor=010308" />

<br/><br/>

<table>
  <tr>
    <td align="center" width="100%">
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
          <td>Greater Noida Institute of Technology <b>(GNIOT)</b></td>
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
          <td>🖥️ <b>Frontend</b></td>
          <td><a href="https://aegis-traffic.streamlit.app/">aegis-traffic.streamlit.app</a></td>
        </tr>
        <tr>
          <td>⚙️ <b>Backend API</b></td>
          <td><a href="https://aegis-traffic.vercel.app">aegis-traffic.vercel.app</a></td>
        </tr>
      </table>
    </td>
  </tr>
</table>

<br/>

<img src="https://img.shields.io/badge/B.Tech-CSE%20%7C%20AI%20%26%20ML-00f0ff?style=flat-square&labelColor=010308"/>
<img src="https://img.shields.io/badge/GNIOT-Greater%20Noida%20Institute%20of%20Technology-10b981?style=flat-square"/>
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
<img src="https://img.shields.io/badge/ANPR-Plate%20Recognition-a855f7?style=flat-square"/>
<img src="https://img.shields.io/badge/Violation%20Detection-Traffic%20Enforcement-ef4444?style=flat-square"/>

<br/><br/>

**⭐ Star this repo if AEGIS-Traffic helped your smart city research!**

</div>