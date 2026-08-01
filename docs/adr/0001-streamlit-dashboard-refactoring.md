# ADR 0001: Streamlit Dashboard Refactoring & Modularization

## Context
The AEGIS-Traffic Streamlit dashboard grew into a 2,600+ line single file controller (`app.py`), containing all authentication modals, CSS declarations, metric components, chart definitions, page views, and API calls. This created cognitive overload for maintainers and hindered scalability.

## Decision
We decomposed `app.py` into a clean multi-module architecture:
1. `dashboard/pages/`: Modular page views (`overview`, `analytics`, `maps`, `violations`, `anpr`, `copilot`, `reports`, `admin`, `settings`).
2. `dashboard/components/`: Reusable UI elements (`navbar`, `sidebar`, `widgets`).
3. `dashboard/services/`: Centralized `AegisClient` API wrapper, structured file/console logger (`logs/frontend.log`), and caching utilities.
4. `dashboard/theme/`: Dedicated CSS stylesheets (`style.css`, `dashboard.css`, `components.css`) injected dynamically via `@st.cache_data`.

## Consequences
- Reduces main controller (`app.py`) from 2,639 lines down to ~90 lines.
- Enhances maintainability, testability, and code readability.
- Retains fast page re-renders through cached theme loading and API client session reuse.
