# AEGIS-Traffic — Architectural & Design Decisions

This document details the key engineering design decisions, trade-offs, and rationale behind the architecture of **AEGIS-Traffic**.

---

## 1. Why FastAPI?
- **Asynchronous ASGI Support**: Native support for Python `async/await` and WebSockets via Starlette, enabling real-time telemetry streaming (`/ws/telemetry`) without thread pool exhaustion.
- **OpenAPI & Automatic Documentation**: Automatic generation of interactive Swagger (`/docs`) and ReDoc (`/redoc`) specifications directly from Pydantic schemas.
- **Low Overhead & Speed**: Benchmarks among the fastest Python frameworks available, matching NodeJS and Go performance characteristics for I/O-bound microservices.
- **Pydantic Data Validation**: Strict runtime type-checking and schema validation at request boundaries.

---

## 2. Why Streamlit?
- **Rapid Operations Prototyping**: Streamlit allows traffic engineers, data scientists, and law enforcement officers to interact with complex Plotly charts, spatial Leaflet maps, and real-time telemetry filters with zero JavaScript frontend boilerplate.
- **Native Session State**: Keeps track of active camera feeds, selected junction nodes, and user auth tokens seamlessly across tab navigations.
- **Python Data Ecosystem Integration**: Direct integration with PyTorch, OpenCV, Pandas, and NumPy for real-time model output visualization.

---

## 3. Why WebSockets?
- **Network Overhead Reduction**: Eliminates HTTP header overhead (500B–1KB per request) when streaming telemetry updates every second.
- **Sub-Second Telemetry Latency**: Delivers vehicle count deltas, speed changes, and emergency alerts instantly to all connected dashboards with minimal jitter.
- **Graceful Fallback**: Implemented automatic HTTP polling fallback if WebSocket connections are blocked by enterprise firewalls or proxies.

---

## 4. Why ByteTrack?
- **Occlusion Resilience**: Traditional trackers like SORT or DeepSORT rely heavily on visual re-identification embeddings. When vehicles pass under bridges, trees, or behind large buses, visual embeddings fail. ByteTrack retains tracks by utilizing low-confidence detection boxes and Kalman Filter state propagation.
- **High FPS Performance**: Performs tracking association using Kalman Filter motion prediction and IoU matching without running heavy visual feature extractor deep models on every frame, preserving 30+ FPS on edge devices.

---

## 5. Why Hybrid Time-Series Forecasting?
- **Low Computational Footprint**: Combines exponential smoothing with diurnal commuter peak curves (8–10 AM & 5–8 PM) rather than heavy recurrent neural networks (LSTM/Transformers) that introduce multi-second inference latency.
- **Multi-Horizon Support**: Delivers 5 prediction points (`Now`, `+15m`, `+30m`, `+1h`, `Tomorrow`) in under 18ms with explicit confidence intervals.
- **Explainability**: Enables direct mathematical attribution for feature contributions (historical density, precipitation, acoustic anomalies).

---

## 6. Why Modular Decoupled Architecture?
- **Maintainability & Testability**: Decoupled modules (`cctv_analytics.py`, `forecasting.py`, `explainability.py`, `benchmark_engine.py`) allow unit testing without booting the web framework or database.
- **Independent Scaling**: Inference pipelines can be worker-isolated or GPU-offloaded without refactoring core API routes.
- **Extensibility**: New computer vision or NLP models can be swapped into the pipeline with zero breaking changes to existing consumer dashboards.

---

## 7. Architectural Complexity Management (What We Decided NOT to Add)
To keep the system performant, maintainable, and deployable on single-node edge instances without bloated infrastructure:
- **No Heavy Message Queues (Kafka / RabbitMQ)**: In-memory async queues and WebSockets provide sub-second latency without the operational overhead of a multi-node Zookeeper/Kafka cluster.
- **No Kubernetes / Service Mesh**: Docker Compose and single-container edge deployments avoid unnecessary sidecar container overhead for edge smart city gateways.
