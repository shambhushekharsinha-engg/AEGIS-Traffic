from typing import Dict, Any

class WhatIfSimulator:
    def __init__(self):
        # Deterministic simulation constants
        self.arrival_rate_veh_per_min = 15.0 # lambda
        self.service_rate_veh_per_min_green = 30.0 # mu
        
    def simulate_signal_change(
        self, 
        current_green_sec: int, 
        proposed_green_sec: int, 
        cycle_length_sec: int,
        current_queue_m: float
    ) -> Dict[str, Any]:
        """
        Deterministic simulation of queue and delay based on signal timing changes.
        Uses simplistic queuing logic for demonstration.
        """
        # Current capacity per cycle
        current_green_ratio = current_green_sec / cycle_length_sec
        current_capacity = self.service_rate_veh_per_min_green * current_green_ratio
        
        # Proposed capacity per cycle
        proposed_green_ratio = proposed_green_sec / cycle_length_sec
        proposed_capacity = self.service_rate_veh_per_min_green * proposed_green_ratio
        
        # Simple heuristic: ratio of capacity improvement inversely affects queue
        capacity_ratio = current_capacity / proposed_capacity if proposed_capacity > 0 else 1.0
        
        projected_queue_m = max(0.0, current_queue_m * capacity_ratio)
        queue_reduction_percent = 0.0
        if current_queue_m > 0:
            queue_reduction_percent = ((current_queue_m - projected_queue_m) / current_queue_m) * 100.0
            
        # Delay roughly proportional to queue
        delay_reduction_percent = queue_reduction_percent
        
        # Throughput increases directly with capacity, capped by arrival rate
        current_throughput = min(self.arrival_rate_veh_per_min, current_capacity)
        proposed_throughput = min(self.arrival_rate_veh_per_min, proposed_capacity)
        throughput_increase_percent = 0.0
        if current_throughput > 0:
            throughput_increase_percent = ((proposed_throughput - current_throughput) / current_throughput) * 100.0
            
        return {
            "scenario": {
                "current_green_sec": current_green_sec,
                "proposed_green_sec": proposed_green_sec
            },
            "projected": {
                "queue_length_m": round(projected_queue_m, 1),
                "queue_reduction_percent": round(queue_reduction_percent, 1),
                "delay_reduction_percent": round(delay_reduction_percent, 1),
                "throughput_increase_percent": round(throughput_increase_percent, 1)
            },
            "confidence": "Medium",
            "assumptions": {
                "arrival_rate_veh_per_min": self.arrival_rate_veh_per_min,
                "service_rate_veh_per_min_green": self.service_rate_veh_per_min_green,
                "deterministic_model": "Simplified deterministic capacity ratio queuing model."
            }
        }
        
    def compare_scenarios(self, base_green_sec: int, cycle_length_sec: int, current_queue_m: float) -> list[Dict[str, Any]]:
        scenarios = []
        # Compare +0s (current), +10s, +20s
        for proposed in [base_green_sec, base_green_sec + 10, base_green_sec + 20]:
            if proposed < cycle_length_sec:
                sim = self.simulate_signal_change(base_green_sec, proposed, cycle_length_sec, current_queue_m)
                scenarios.append(sim)
        return scenarios

simulator = WhatIfSimulator()
