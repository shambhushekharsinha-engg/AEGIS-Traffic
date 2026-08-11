from app.services.simulator.model import simulator


def test_simulator_determinism():
    """
    Determinism test:
    simulate(input, +15s) == simulate(input, +15s)
    """
    base_green = 45
    proposed = 60
    cycle = 105
    queue = 420.0

    result_1 = simulator.simulate_signal_change(base_green, proposed, cycle, queue)
    result_2 = simulator.simulate_signal_change(base_green, proposed, cycle, queue)

    assert (
        result_1 == result_2
    ), "Simulator should produce identical output for identical input."


def test_queue_never_negative():
    """
    Simulation cannot produce negative queue lengths.
    """
    result = simulator.simulate_signal_change(30, 100, 120, 10.0)
    assert (
        result["projected"]["queue_length_m"] >= 0
    ), "Queue length cannot be negative."
