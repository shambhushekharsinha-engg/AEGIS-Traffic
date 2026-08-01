"""
AEGIS-Traffic — Centralized API Client (AegisClient)
Provides standard HTTP operations, auth header management, retry strategies, and structured logging.
"""
import os
import requests
from typing import Dict, Any, Optional
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from dashboard.services.logger import logger


class AegisAPIError(Exception):
    """Custom exception raised for Aegis API operational failures."""
    def __init__(self, message: str, status_code: Optional[int] = None, detail: Any = None):
        if detail:
            if isinstance(detail, dict):
                err_msg = detail.get("detail", detail.get("error", str(detail)))
            elif isinstance(detail, list):
                err_msg = detail[0].get("msg", str(detail[0])) if detail else str(detail)
            else:
                err_msg = str(detail)
            formatted = f"{message}: {err_msg}"
        else:
            formatted = message
        super().__init__(formatted)
        self.message = formatted
        self.status_code = status_code
        self.detail = detail


class AegisClient:
    """Centralized HTTP Client for backend communication."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 8):
        self.base_url = (base_url or os.environ.get("AEGIS_BACKEND_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure connection pooling and retries
        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def is_alive(self) -> bool:
        """Checks if backend service is reachable."""
        try:
            r = self.session.get(f"{self.base_url}/", timeout=2)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticates user against FastAPI auth module."""
        url = f"{self.base_url}/api/v1/auth/login"
        try:
            logger.info(f"Authenticating user: {username}")
            res = self.session.post(url, json={"username": username, "password": password}, timeout=self.timeout)
            if res.status_code == 200:
                logger.info(f"Authentication successful for {username}")
                return res.json()
            
            try:
                detail = res.json().get("detail", "Authentication failed.")
            except Exception:
                detail = res.text or "Access denied."
            logger.warning(f"Login failed for {username}: {detail}")
            raise AegisAPIError("Authentication Error", status_code=res.status_code, detail=detail)
        except requests.RequestException as e:
            logger.exception(f"Connection error during login for {username}: {e}")
            raise AegisAPIError("Backend microservice offline on port 8000. Please start the FastAPI server first.", detail=str(e))

    def register(self, username: str, password: str, role: str) -> Dict[str, Any]:
        """Registers new operator credentials."""
        url = f"{self.base_url}/api/v1/auth/register"
        try:
            logger.info(f"Registering new user: {username} with role: {role}")
            res = self.session.post(url, json={"username": username, "password": password, "role": role}, timeout=self.timeout)
            if res.status_code == 200:
                return res.json()
            try:
                detail = res.json().get("detail", "Registration failed.")
            except Exception:
                detail = res.text or "Registration failed."
            raise AegisAPIError("Registration Error", status_code=res.status_code, detail=detail)
        except requests.RequestException as e:
            logger.exception(f"Connection error during registration for {username}: {e}")
            raise AegisAPIError("Backend microservice offline on port 8000.", detail=str(e))

    def get_dashboard_summary(self, token: str) -> Dict[str, Any]:
        """Fetches live dashboard summary stats."""
        url = f"{self.base_url}/api/v1/dashboard/summary"
        try:
            res = self.session.get(url, headers=self._get_headers(token), timeout=self.timeout)
            if res.status_code == 200:
                return res.json()
            return {}
        except requests.RequestException as e:
            logger.error(f"Failed to fetch dashboard summary: {e}")
            return {}

    def get_history(self, token: str) -> Dict[str, Any]:
        """Fetches historical traffic flow data."""
        url = f"{self.base_url}/api/v1/history"
        try:
            res = self.session.get(url, headers=self._get_headers(token), timeout=self.timeout)
            if res.status_code == 200:
                return res.json()
            return {}
        except requests.RequestException as e:
            logger.error(f"Failed to fetch traffic history: {e}")
            return {}

    def chat_copilot(self, query: str, token: str) -> Dict[str, Any]:
        """Sends operational prompt to AI Copilot engine."""
        url = f"{self.base_url}/api/v1/chat"
        try:
            res = self.session.post(url, json={"message": query}, headers=self._get_headers(token), timeout=12)
            if res.status_code == 200:
                return res.json()
            return {"reply": "Unable to connect to AI Copilot inference backend."}
        except requests.RequestException as e:
            logger.error(f"Copilot API error: {e}")
            return {"reply": "Copilot service unavailable."}

    def get_violations(self, token: str) -> Dict[str, Any]:
        """Fetches traffic violations ledger."""
        url = f"{self.base_url}/api/v1/violations"
        try:
            res = self.session.get(url, headers=self._get_headers(token), timeout=self.timeout)
            if res.status_code == 200:
                return res.json()
            return {}
        except requests.RequestException as e:
            logger.error(f"Failed to fetch violations: {e}")
            return {}

    def get_anpr(self, token: str) -> Dict[str, Any]:
        """Fetches ANPR detection records."""
        url = f"{self.base_url}/api/v1/anpr"
        try:
            res = self.session.get(url, headers=self._get_headers(token), timeout=self.timeout)
            if res.status_code == 200:
                return res.json()
            return {}
        except requests.RequestException as e:
            logger.error(f"Failed to fetch ANPR records: {e}")
            return {}
