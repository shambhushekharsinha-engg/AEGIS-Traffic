from typing import Dict, Any


class WhatIfSimulator:
    def __init__(self):
        # Deterministic simulation constants
        self.arrival_rate_veh_per_min = 15.0  # lambda
        self.service_rate_veh_per_min_green = 30.0  # mu

    def simulate_signal_change(
        self,
        current_green_sec: int,
        proposed_green_sec: int,
        cycle_length_sec: int,
        current_queue_m: float,
    ) -> Dict[str, Any]:
        """
        Deterministic simulation of queue and delay based on signal timing changes.
        Projects queue length over 5 consecutive signal cycles.
        """
        num_cycles = 5

        # Calculate capacities (vehicles per cycle)
        current_green_ratio = current_green_sec / cycle_length_sec
        current_capacity = (
            self.service_rate_veh_per_min_green
            * (cycle_length_sec / 60.0)
            * current_green_ratio
        )

        proposed_green_ratio = proposed_green_sec / cycle_length_sec
        proposed_capacity = (
            self.service_rate_veh_per_min_green
            * (cycle_length_sec / 60.0)
            * proposed_green_ratio
        )

        # Arrivals per cycle
        arrivals_per_cycle = self.arrival_rate_veh_per_min * (cycle_length_sec / 60.0)

        # We assume 1 vehicle roughly equates to 5 meters of queue
        M_PER_VEHICLE = 5.0

        initial_vehicles_queued = current_queue_m / M_PER_VEHICLE

        current_trajectory = [initial_vehicles_queued]
        proposed_trajectory = [initial_vehicles_queued]

        curr_q = initial_vehicles_queued
        prop_q = initial_vehicles_queued

        for _ in range(num_cycles):
            curr_q = max(0.0, curr_q + arrivals_per_cycle - current_capacity)
            current_trajectory.append(curr_q)

            prop_q = max(0.0, prop_q + arrivals_per_cycle - proposed_capacity)
            proposed_trajectory.append(prop_q)

        final_current_queue_m = current_trajectory[-1] * M_PER_VEHICLE
        final_proposed_queue_m = proposed_trajectory[-1] * M_PER_VEHICLE

        queue_reduction_percent = 0.0
        if final_current_queue_m > 0:
            queue_reduction_percent = (
                (final_current_queue_m - final_proposed_queue_m) / final_current_queue_m
            ) * 100.0
        elif (
            current_queue_m > 0 and final_current_queue_m == final_proposed_queue_m == 0
        ):
            queue_reduction_percent = 100.0

        return {
            "scenario": {
                "current_green_sec": current_green_sec,
                "proposed_green_sec": proposed_green_sec,
            },
            "projected": {
                "queue_length_m": round(final_proposed_queue_m, 1),
                "queue_reduction_percent": round(queue_reduction_percent, 1),
                "delay_reduction_percent": round(
                    queue_reduction_percent, 1
                ),  # Roughly proportional
                "throughput_increase_percent": round(
                    (
                        ((proposed_capacity - current_capacity) / current_capacity)
                        * 100
                        if current_capacity > 0
                        else 0
                    ),
                    1,
                ),
                "trajectory_m": [
                    round(q * M_PER_VEHICLE, 1) for q in proposed_trajectory
                ],
            },
            "confidence": "Medium",
            "assumptions": {
                "arrival_rate_veh_per_min": self.arrival_rate_veh_per_min,
                "service_rate_veh_per_min_green": self.service_rate_veh_per_min_green,
                "deterministic_model": "Multi-cycle (n=5) deterministic evolution.",
            },
        }

    def compare_scenarios(
        self, base_green_sec: int, cycle_length_sec: int, current_queue_m: float
    ) -> list[Dict[str, Any]]:
        scenarios = []
        # Compare +0s (current), +10s, +20s
        for proposed in [base_green_sec, base_green_sec + 10, base_green_sec + 20]:
            if proposed < cycle_length_sec:
                sim = self.simulate_signal_change(
                    base_green_sec, proposed, cycle_length_sec, current_queue_m
                )
                scenarios.append(sim)
        return scenarios


simulator = WhatIfSimulator()
