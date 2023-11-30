from qiskit import QuantumRegister
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error, thermal_relaxation_error


class Unified_Noise_Model:
    """Unified Noise model"""

    def __init__(self):
        """Create and empty noise model."""
        self.noise_model = NoiseModel()

        self.one_qubit_gates_depolarizing_noise_channel = None
        self.two_qubits_gates_depolarizing_noise_channel = None

        self.one_qubit_gates_relaxation_dephasing_noise_channel = []
        self.two_qubits_gates_relaxation_dephasing_noise_channel = []

    def add_all_noise_channels(
        self,
        state_preparation_error_prob,
        measurement_error_prob,
        state_preparation_error_gate,
        depolarizing_prob,
        one_qubit_gates,
        one_qubit_gates_times,
        two_qubits_gates,
        two_qubits_gates_times,
        qubits,
        qubits_T1,
        qubits_T2,
    ):
        """Add the three noise channels to the UNM:
        1- Depolarizing Channel.
        2- SPAM Channel.
        3- Relaxation and Dephasing Channel.

        For state_preparation_error_gate.In your circuit, this gate must appear,
        in each qubit, after the state preparation. This gate must have a
        different label settled so as to this channel can works. It is recommended
        to label the gate as 'x_StatePreparation'.
        !!!TWO_QUBITS_GATES_TIME ESTA ACTUALMENTE SIMPLIFICADO, RECIBE UN FLOAT[]

        Args:
            state_preparation_error_prob(float): probability of error during the state preparation.
            measurement_error_prob(float): probability of error during measurement.
            state_preparation_error_gate(Gate):the X gate for the noise in the state preparation.
            depolarizing_prob (float): probability of a depolarizing error to happen.
            one_qubit_gates: list of strings representing one qubit gates with noise.
            one_qubit_gates_times(float[qubits][gates]):list execution times(qubit,one qubit gate).
            two_qubits_gates:list of strings representing two qubits gates with noise.
            two_qubits_gates_times :list execution times(qubit,2 qubits gate).
            qubits (QuantumRegister): Qubits of the circuit to which add noise.
            qubits_t1: list of floats that represents T1 for each of the qubits.
            qubits_t2: list of floats that represents T2 for each of the qubits.
        """

        # Creates the depolarizing and relaxation and dephasing channels
        self.create_depolarizing_channel(depolarizing_prob)
        self.create_relaxation_dephasing_channel(
            qubits,
            qubits_T1,
            qubits_T2,
            one_qubit_gates,
            one_qubit_gates_times,
            two_qubits_gates,
            two_qubits_gates_times,
        )

        # Compose the depolarizing and relaxation and dephasing channels.
        # p --after channels-->RD(D(p)) where:
        # * RD() = relaxation and dephasing channel
        # * D() = depolarizing channel
        for qubit in qubits:
            for gate in range(len(one_qubit_gates)):
                error = self.one_qubit_gates_depolarizing_noise_channel.compose(
                    self.one_qubit_gates_relaxation_dephasing_noise_channel[qubit][gate],
                )
                self.noise_model.add_quantum_error(error, one_qubit_gates[gate], [qubit])

            for second_qubit in qubits:
                for gate in range(len(two_qubits_gates)):
                    error = self.two_qubits_gates_depolarizing_noise_channel.compose(
                        self.two_qubits_gates_relaxation_dephasing_noise_channel[qubit][
                            second_qubit
                        ][gate],
                    )
                    self.noise_model.add_quantum_error(
                        error,
                        two_qubits_gates[gate],
                        [qubit, second_qubit],
                    )

        self.add_spam_channel(
            state_preparation_error_prob,
            measurement_error_prob,
            state_preparation_error_gate,
        )

    def add_spam_channel(
        self,
        statePreparation_error_prob=-1,
        measurement_error_prob=-1,
        statePreparation_error_gate=None,
    ):
        """Add the SPAM channel to the UNM

        Args:
        statePreparation_error_prob(float): probability of error during the state preparation.
        measurement_error_prob(float): probability of error during measurement.
        statePreparation_error_gate(Gate): the X gate that will represent the noise
                                           after the state preparation.In your circuit,
                                           this gate must appear, in each qubit,
                                           after the state preparation.
                                           This gate must have a different label settled
                                           so as to this channel can works. It is recommended
                                           to label the gate as 'x_StatePreparation'.

        Considerations:
        the error probabilities are the same for each qubit. In future updates, it will be possible
        to set different statePreparation_error_prob and measurement_error_prob for each qubit.
        """

        # state preparation errors
        if statePreparation_error_prob >= 0:
            statePreparation_error = pauli_error(
                [("I", statePreparation_error_prob), ("X", 1 - statePreparation_error_prob)],
            )
            self.noise_model.add_all_qubit_quantum_error(
                statePreparation_error,
                statePreparation_error_gate.label,
            )
            self.noise_model.add_basis_gates(["x"])

        if measurement_error_prob >= 0:
            measurement_error = pauli_error(
                [("X", measurement_error_prob), ("I", 1 - measurement_error_prob)],
            )
            self.noise_model.add_all_qubit_quantum_error(measurement_error, "measure")

    def add_depolarizing_channel(
        self,
        depolarizing_prob,
        one_qubit_gates,
        two_qubits_gates,
        add_one_qubit_gates_noise=True,
        add_two_qubits_gates_noise=True,
    ):
        """Adds a depolarizing channel to the model.

        Args:
            depolarizing_prob(float): probability of depolarizing error to happen
            one_qubit_gates: list of strings representing one qubit gates with noise
            two_qubits_gates:list of strings representing two qubits gates with noise.
            add_one_qubit_gates_noise(Boolean): defines if the channel will add noise to
                                                one qubit gates
            add_two_qubits_gates_noise(Boolean): defines if the channel will add noise to
                                                 two qubits gates

        Considerations:
        the error probabilities are the same for each qubit,and for two qubits and
        one qubit gates. In future updates, it will be possible to set different probabilties
        for each qubit and amount of qubits.
        """

        # Creates and save the depolarizing channel
        self.create_depolarizing_channel(
            depolarizing_prob,
            add_one_qubit_gates_noise,
            add_two_qubits_gates_noise,
        )

        # Adds the depolarizing channel to the model
        self.noise_model.add_all_qubit_quantum_error(
            self.one_qubit_gates_depolarizing_noise_channel,
            one_qubit_gates,
        )
        self.noise_model.add_all_qubit_quantum_error(
            self.two_qubits_gates_depolarizing_noise_channel,
            two_qubits_gates,
        )

    def create_depolarizing_channel(
        self,
        depolarizing_prob,
        add_one_qubit_gates_noise=True,
        add_two_qubits_gates_noise=True,
    ):
        """Create a depolarizing channel and save it.

        Args:
            depolarizing_prob(float): probability of depolarizing error to happen
            add_one_qubit_gates_noise(Boolean): defines if the channel will add noise to
                                                one qubit gates
            add_two_qubits_gates_noise(Boolean): defines if the channel will add noise to
                                                 two qubits gates

        Considerations:
        the error probabilities are the same for each qubit,and for two qubits and
        one qubit gates. In future updates, it will be possible to set different probabilties
        for each qubit and amount of qubits.
        """
        # Noise to one qubit gates
        if add_one_qubit_gates_noise:
            error = depolarizing_error(depolarizing_prob, 1)
            self.one_qubit_gates_depolarizing_noise_channel = error
        # Noise to two qubits gates
        if add_two_qubits_gates_noise:
            error = depolarizing_error(depolarizing_prob, 2)
            self.two_qubits_gates_depolarizing_noise_channel = error

    def add_relaxation_dephasing_channel(
        self,
        qubits: QuantumRegister,
        qubits_T1: list,
        qubits_T2: list,
        one_qubit_gates: list,
        one_qubit_gates_times: list,
        two_qubits_gates: list,
        two_qubits_gates_times: list,
    ):
        self.create_relaxation_dephasing_channel(
            qubits,
            qubits_T1,
            qubits_T2,
            one_qubit_gates,
            one_qubit_gates_times,
            two_qubits_gates,
            two_qubits_gates_times,
        )

        for qubit in qubits:
            for gate in range(len(one_qubit_gates)):
                error = self.one_qubit_gates_relaxation_dephasing_noise_channel[qubit][gate]
                self.noise_model.add_quantum_error(error, one_qubit_gates[gate], [qubit])

            for second_qubit in qubits:
                for gate in range(len(two_qubits_gates)):
                    error = self.two_qubits_gates_relaxation_dephasing_noise_channel[qubit][
                        second_qubit
                    ][gate]
                    self.noise_model.add_quantum_error(
                        error,
                        two_qubits_gates[gate],
                        [qubit, second_qubit],
                    )

    def create_relaxation_dephasing_channel(
        self,
        qubits: QuantumRegister,
        qubits_T1: list,
        qubits_T2: list,
        one_qubit_gates: list,
        one_qubit_gates_times: list,
        two_qubits_gates: list,
        two_qubits_gates_times: list,
    ):
        """Create a relaxation and dephasing channel and save it as a list[qubit][][].

        Args:
            qubits (QuantumRegister): Qubits of the circuit to which add noise.
            qubits_T1: list of floats that represents T1 for each
                              of the qubits.
            qubits_T2: list of floats that represents T2 for each
                               of the qubits.
            one_qubit_gates: list of strings representing single gates
                                   with noise.
            one_qubit_gates_times(float[qubits][gates]): list of execution times
                                                for each (qubit,single gate).
            two_qubits_gates:list of strings representing double gates with noise.
            two_qubits_gates_times(float[qubits][gates]):list of execution times
                                                 for each (qubit,double gate).
            !!!DOUBLE_GATES_TIME ESTA ACTUALMENTE SIMPLIFICADO, RECIBE UN FLOAT[]
        """

        # For each qubit, we add it respective one_qubit and two_qubit gates noise
        for qubit in qubits:
            # Here, we add the one_qubit gates noise
            self.one_qubit_gates_relaxation_dephasing_noise_channel.append([])
            for gate in range(len(one_qubit_gates)):
                error = thermal_relaxation_error(
                    qubits_T1[qubit],
                    qubits_T2[qubit],
                    one_qubit_gates_times[qubit][gate],
                )
                self.one_qubit_gates_relaxation_dephasing_noise_channel[qubit].append(error)

            # Here, we add the two_qubit gates noise
            self.two_qubits_gates_relaxation_dephasing_noise_channel.append([])
            for second_qubit in qubits:
                self.two_qubits_gates_relaxation_dephasing_noise_channel[qubit].append([])
                for gate in range(len(two_qubits_gates)):
                    error = thermal_relaxation_error(
                        qubits_T1[qubit],
                        qubits_T2[qubit],
                        two_qubits_gates_times[gate],
                    ).expand(
                        thermal_relaxation_error(
                            qubits_T1[second_qubit],
                            qubits_T2[second_qubit],
                            two_qubits_gates_times[gate],
                        ),
                    )
                    self.two_qubits_gates_relaxation_dephasing_noise_channel[qubit][
                        second_qubit
                    ].append(error)
