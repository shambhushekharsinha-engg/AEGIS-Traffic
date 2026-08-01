"""
AEGIS-Traffic — Time-Series Multi-Horizon Traffic Forecast Engine
Provides time-series forecasting across Now, 15m, 30m, 1h, and 24h (Tomorrow) horizons.
"""
import time
import math
import numpy as np

class TimeSeriesForecastEngine:
    def __init__(self):
        pass

    def generate_timeline_forecast(self, current_density: float = 62.5, location_name: str = "Connaught Place") -> dict:
        """
        Generates traffic time-series predictions with confidence intervals.
        Horizons: Now (0m), 15m, 30m, 60m, 24h (Tomorrow Morning).
        """
        t = time.time()
        # Simulated trend parameters based on diurnal curve
        hour_of_day = (time.localtime(t).tm_hour + time.localtime(t).tm_min / 60.0)
        
        # Diurnal peak factor curve (morning 8-10am peak, evening 5-8pm peak)
        morning_peak = math.exp(-((hour_of_day - 9.0) ** 2) / 4.0)
        evening_peak = math.exp(-((hour_of_day - 18.0) ** 2) / 6.0)
        diurnal_factor = 0.4 + 0.6 * (morning_peak + evening_peak)

        base_val = current_density

        horizons = [
            {"label": "Now", "offset_min": 0, "multiplier": 1.0, "confidence_std": 2.0},
            {"label": "+15 min", "offset_min": 15, "multiplier": 1.05 if diurnal_factor > 0.6 else 0.95, "confidence_std": 4.5},
            {"label": "+30 min", "offset_min": 30, "multiplier": 1.12 if diurnal_factor > 0.6 else 0.88, "confidence_std": 7.0},
            {"label": "+1 hour", "offset_min": 60, "multiplier": 1.20 if diurnal_factor > 0.6 else 0.75, "confidence_std": 10.5},
            {"label": "Tomorrow Morning", "offset_min": 1440, "multiplier": 1.35, "confidence_std": 14.0},
        ]

        timeline = []
        for h in horizons:
            pred_density = min(98.0, max(10.0, round(base_val * h["multiplier"] + np.random.uniform(-1.5, 1.5), 1)))
            lower_bound = max(5.0, round(pred_density - h["confidence_std"] * 1.5, 1))
            upper_bound = min(100.0, round(pred_density + h["confidence_std"] * 1.5, 1))
            confidence_pct = max(70, round(98.0 - (h["offset_min"] / 1440.0) * 22.0, 1))
            
            if pred_density > 75:
                level = "HIGH CONGESTION"
            elif pred_density > 45:
                level = "MODERATE TRAFFIC"
            else:
                level = "CLEAR FLOW"

            timeline.append({
                "label": h["label"],
                "offset_minutes": h["offset_min"],
                "predicted_density_pct": pred_density,
                "confidence_interval": [lower_bound, upper_bound],
                "confidence_pct": confidence_pct,
                "status_level": level,
                "projected_avg_speed_kmh": round(60.0 / (1.0 + 0.03 * (pred_density / 2.0)), 1)
            })

        return {
            "location": location_name,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_density_pct": current_density,
            "timeline": timeline
        }

forecasting_engine = TimeSeriesForecastEngine()
