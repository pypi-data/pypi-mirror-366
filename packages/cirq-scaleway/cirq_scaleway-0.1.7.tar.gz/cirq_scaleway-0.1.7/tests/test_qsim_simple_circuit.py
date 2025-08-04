import os

import cirq

from cirq_scaleway import ScalewayQuantumService


def test_qsim_simple_circuit():
    service = ScalewayQuantumService(
        project_id=os.environ["CIRQ_SCALEWAY_PROJECT_ID"],
        secret_key=os.environ["CIRQ_SCALEWAY_SECRET_KEY"],
        url=os.environ["CIRQ_SCALEWAY_API_URL"],
    )

    qsim_simulator = service.device(name="qsim_simulation_pop_c16m128")

    assert qsim_simulator is not None

    with qsim_simulator.create_session() as session:
        qubit = cirq.GridQubit(0, 0)
        circuit = cirq.Circuit(cirq.X(qubit) ** 0.5, cirq.measure(qubit, key="m"))

        # Run the circuit on the device
        shots_count = 100
        result = session.run(circuit, repetitions=shots_count)

        assert result is not None
        assert result.repetitions == shots_count
