# ADR 0003: Security Headers Middleware & Caching Strategy

## Context
Production web services require protection against common web vulnerabilities (XSS, Clickjacking, MIME sniffing, protocol downgrade attacks). Additionally, frequent UI reruns in Streamlit can trigger repetitive disk reads and network roundtrips.

## Decision
1. **Security Headers Middleware**: Implemented `SecurityHeadersMiddleware` in FastAPI to automatically inject:
   - `Content-Security-Policy` (CSP)
   - `Strict-Transport-Security` (HSTS)
   - `X-Frame-Options: DENY`
   - `X-Content-Type-Options: nosniff`
   - `X-XSS-Protection: 1; mode=block`
2. **Caching Strategy**: Leveraged Streamlit's `@st.cache_resource` for API client singleton re-use and `@st.cache_data` for external CSS loading, geo-currency lookups, and analytics calculations.

## Consequences
- Achieves enterprise-grade HTTP security compliance.
- Significantly boosts Streamlit dashboard render speeds and eliminates redundant stylesheet reads.
