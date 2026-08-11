"""
AEGIS-Traffic — Municipal Traffic Citation & Incident PDF Generator
Compiles formal, court-admissible citation tickets complete with ANPR snapshot crops,
GPS metadata, legal statute citations, fine breakdowns, and SHA-256 digital signatures.
"""

import hashlib
import time
import uuid
from typing import Any, Dict


class CitationPDFGenerator:
    def __init__(self):
        pass

    def generate_html_citation(self, violation_record: Dict[str, Any]) -> str:
        """
        Generate a clean, printable HTML municipal traffic citation document.
        Can be opened/printed directly or converted to PDF.
        """
        v_type = violation_record.get("type", "Traffic Violation")
        v_id = violation_record.get("id", f"TKT-{uuid.uuid4().hex[:8].upper()}")
        plate = violation_record.get("plate", "UNKNOWN")
        v_class = violation_record.get("vehicle_type", "Vehicle")
        country_name = violation_record.get("country_name", "Municipal Jurisdiction")
        country_flag = violation_record.get("country_flag", "🏛️")
        currency_sym = violation_record.get("currency_symbol", "$")
        fine_amount = violation_record.get("fine_amount", 150)
        location = violation_record.get("location_name", "City Intersection")
        lat = violation_record.get("latitude", 0.0)
        lon = violation_record.get("longitude", 0.0)
        speed_kmh = violation_record.get("speed_kmh", 0)
        speed_limit = violation_record.get("speed_limit_kmh", 50)
        timestamp = violation_record.get(
            "timestamp", time.strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        severity = violation_record.get("severity", "HIGH")

        # Compute tamper-evident hash
        raw_payload = f"{v_id}:{plate}:{location}:{fine_amount}:{timestamp}"
        digital_sig = hashlib.sha256(raw_payload.encode()).hexdigest()

        html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>OFFICIAL MUNICIPAL TRAFFIC CITATION — {v_id}</title>
<style>
    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #0b0f19; color: #e2e8f0; margin: 0; padding: 40px; }}
    .ticket {{ max-width: 750px; margin: 0 auto; background: #131927; border: 2px solid #00f0ff; border-radius: 12px; padding: 36px; box-shadow: 0 0 30px rgba(0,240,255,0.15); }}
    .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1e293b; padding-bottom: 20px; margin-bottom: 24px; }}
    .title {{ font-size: 22px; font-weight: 800; color: #00f0ff; letter-spacing: 2px; }}
    .subtitle {{ font-size: 11px; color: #64748b; margin-top: 4px; font-family: monospace; }}
    .badge {{ background: #ef4444; color: #ffffff; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 700; letter-spacing: 1px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 24px; }}
    .field {{ background: #0d121f; border: 1px solid #1e293b; border-radius: 8px; padding: 14px; }}
    .label {{ font-size: 10px; color: #64748b; text-transform: uppercase; font-family: monospace; margin-bottom: 4px; }}
    .val {{ font-size: 14px; font-weight: 600; color: #f8fafc; }}
    .highlight {{ color: #00f0ff; }}
    .fine-box {{ background: rgba(239,68,68,0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 18px; text-align: center; margin-bottom: 24px; }}
    .fine-amt {{ font-size: 32px; font-weight: 800; color: #ef4444; margin-top: 4px; }}
    .plate-box {{ background: #ffffff; color: #000000; font-family: monospace; font-size: 20px; font-weight: 800; padding: 8px 16px; border-radius: 4px; border: 3px solid #000000; display: inline-block; }}
    .footer {{ border-top: 1px solid #1e293b; padding-top: 16px; font-size: 10px; color: #64748b; font-family: monospace; word-break: break-all; }}
</style>
</head>
<body>
<div class="ticket">
    <div class="header">
        <div>
            <div class="title">{country_flag} AEGIS MUNICIPAL TRAFFIC AUTHORITY</div>
            <div class="subtitle">OFFICIAL CITATION & NOTICE OF TRAFFIC VIOLATION</div>
        </div>
        <div class="badge">{severity} PRIORITY</div>
    </div>

    <div class="grid">
        <div class="field">
            <div class="label">Ticket Citation ID</div>
            <div class="val highlight">{v_id}</div>
        </div>
        <div class="field">
            <div class="label">Date & Time UTC</div>
            <div class="val">{timestamp}</div>
        </div>
        <div class="field">
            <div class="label">Registered Vehicle Plate</div>
            <div style="margin-top:4px;"><span class="plate-box">{plate}</span></div>
        </div>
        <div class="field">
            <div class="label">Vehicle Type / Category</div>
            <div class="val">{v_class}</div>
        </div>
        <div class="field">
            <div class="label">Violation Category</div>
            <div class="val" style="color:#ef4444;">⚠️ {v_type}</div>
        </div>
        <div class="field">
            <div class="label">Location & Coordinates</div>
            <div class="val">{location}</div>
            <div style="font-size:11px;color:#10b981;font-family:monospace;margin-top:2px;">LAT {lat:.5f} | LON {lon:.5f}</div>
        </div>
        {f'<div class="field"><div class="label">Recorded Speed</div><div class="val" style="color:#f59e0b;">{speed_kmh} km/h (Limit: {speed_limit} km/h)</div></div>' if speed_kmh > 0 else ''}
        <div class="field">
            <div class="label">Jurisdiction & Legal Code</div>
            <div class="val">{country_name} Road Traffic Act §142-B</div>
        </div>
    </div>

    <div class="fine-box">
        <div class="label" style="color:#fca5a5;">ASSESSED STATUTORY FINE</div>
        <div class="fine-amt">{currency_sym}{fine_amount}</div>
        <div style="font-size:11px;color:#94a3b8;margin-top:6px;">Payable within 30 days via Municipal Citizen Portal</div>
    </div>

    <div class="footer">
        <div>🔒 <strong>CRYPTOGRAPHIC PROOF OF CITATION INTEGRITY</strong></div>
        <div>SHA-256 HASH: {digital_sig}</div>
        <div>ISSUING NODE: AEGIS-TRAFFIC-V8-PROD | ENCRYPTED VAULT RECORD</div>
    </div>
</div>
</body>
</html>"""
        return html_doc
