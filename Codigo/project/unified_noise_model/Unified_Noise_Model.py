from qiskit import Aer
from qiskit import QuantumRegister
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error, thermal_relaxation_error
import pandas
import numpy as np
import math

class Unified_Noise_Model:
    """Unified Noise model"""

    def __init__(self):
        """Create and empty noise model."""
        self.noise_model = NoiseModel()

        self.one_qubit_gates_depolarizing_noise_channel = None
        self.two_qubits_gates_depolarizing_noise_channel = None

        self.one_qubit_gates_relaxation_dephasing_noise_channel = []
        self.two_qubits_gates_relaxation_dephasing_noise_channel = []

        # calibration data attributes
        self.device_to_simulate = None
        self.calibration_data = None

        self.single_qubit_basis_gates = None
        self.two_qubits_basis_gates = None
        
        self.qubits = None
        
        self.single_qubit_error_rates = None
        self.two_qubits_error_rates = None
        self.measurement_error_rates = None

        self.T1s = None
        self.T2s = None

    #-------------CALIBRATION DATA------------------------
    
    def print_calibration_data(self):
        print('------------------------------------------------')
        print('BASIS GATES:')
        print(self.noise_model.basis_gates)
        print('------------------------------------------------')
        print('QUBITS:')
        print(self.qubits)
        print('------------------------------------------------')
        print('SINGLE QUBIT ERROR RATES:')
        display(self.single_qubit_error_rates)
        print('------------------------------------------------')
        print('TWO QUBITS ERROR RATES:')
        display(self.two_qubits_error_rates)
        print('------------------------------------------------')
        print('MEASUREMENT ERROR RATES:')
        display(self.measurement_error_rates)
        print('------------------------------------------------')
        print('T1s:')
        print(self.T1s)
        print('------------------------------------------------')
        print('T2s:')
        print(self.T2s)

    def add_calibration_data(self,path,single_qubit_basis_gates,two_qubits_basis_gates,device_to_simulate):
        '''Imports the error rates of the machine as the downloaded csv file. path - the path to the csv file, including
        the name of the csv file and ".csv".'''
    
        colnames = ["Qubit", "Frequency", "T1", "T2", "ReadoutError", "SQError", "TQError"]

        self.noise_model = NoiseModel(basis_gates=(single_qubit_basis_gates+two_qubits_basis_gates))
        self.device_to_simulate = device_to_simulate
        self.single_qubit_basis_gates = single_qubit_basis_gates
        self.two_qubits_basis_gates = two_qubits_basis_gates

        self.calibration_data = pandas.read_csv(path)

        self._getQubits()
        self._getSingleQubitErrorRates()
        self._getTwoQubitErrorRates()
        self._getMeasureErrorRates()
        self._getDecoherenceTimes()

    def _getQubits(self):
        self.qubits = self.calibration_data.Qubit.tolist()
        #for i in range(0, len(self.qubits)):
        #    self.qubits[i] = ("Q" + str(self.qubits[i]))       

    def _getSingleQubitErrorRates(self):
        '''Returns as a dictionary the single qubit error rates, as they appear on ibmq_16_melbourne. NOTE: the 
        values deviate every time the machine gets callibrated.'''
        rates = self.calibration_data.SQError.tolist()

        for i in range(len(rates)):
            if(not math.isnan(rates[i])):
                rates[i] = float(rates[i])
            else:
                rates[i] = 0


        self.single_qubit_error_rates = dict(zip(self.qubits, rates))
    
    def _getTwoQubitErrorRates(self):
        '''Returns as a dictionary the two qubit error rates, as they appear on ibmq_16_melbourne. NOTE: the values 
        deviate every time the machine gets callibrated.'''
        rates = self.calibration_data.TQError.tolist()
        qpairs = []
        qvals = []
        for i in range(0, len(rates)):
            if(type(rates[i]) == str):
                s = rates[i].split(";")
                for j in range(0, len(s)):
                    t = s[j].split(":")
                    qpairs.append(t[0])
                    qvals.append(float(t[1]))
            

    
        self.two_qubits_error_rates = dict(zip(qpairs, qvals))
    
    def _getMeasureErrorRates(self):
        '''Returns as a dictionary the measurement error rates, as they appear on ibmq_16_melbourne. NOTE: the values
        deviate every time the machine gets callibrated'''
        rates = self.calibration_data.ReadoutError.tolist()
        #del rates[0]
        for i in range(len(rates)):
            if(not math.isnan(rates[i])):
                rates[i] = float(rates[i])
            else:
                rates[i] = 0
        self.measurement_error_rates = dict(zip(self.qubits, rates))
    
    def _getDecoherenceTimes(self):
        '''Returns the thermal relaxation time T1 and the qubit dephasing time T2, as given by IBMQ.'''
        t1er = self.calibration_data.T1.tolist()
        t2er = self.calibration_data.T2.tolist()

        for i in range(0, len(t1er)):
            if(not math.isnan(t1er[i])):
                t1er[i] = float(t1er[i]) / float(1000000)
            else:
                t1er[i] = t1er[0]
            if(not math.isnan(t2er[i])):
                t2er[i] = float(t2er[i]) / float(1000000)
            else:
                t2er[i] = t2er[0]

        T1s = np.array(t1er)
        T2s = np.array(t2er)
    
        # Check for error in IBMQ's measurements (i.e it must always be T2 <= 2T1)
        c = 0
        for i in range(0,len(T1s)):
            if (T2s[i] > 2*T1s[i]):
                c = 1
                print("ERROR: incompatible decay rates - Qubit Q" + str(i) + ", T2 =", T2s[i], "and T1 =", T1s[i])
            if (c == 0):
                print(r'Checking decoherence times: all ok')
        
        self.T1s = T1s
        self.T2s = T2s

    def _getSQGateExecutionTime(self,gate):
        '''Returns the average execution time of the single-qubit type gates we are interested in.'''
        # Single qubit gates
        s = [0]*len(self.qubits)
        for i in range(0,len(self.qubits)):
            s[i] = self.device_to_simulate.properties().gate_length(gate, [i])

        return (np.mean(s)*(10**9))

    def _getTQGateExecutionTime(self,gate):
        '''Returns the average execution time of the two-qubit type gates in the circuit.'''
        # Two qubit gates

        t = [0]*len(self.two_qubits_error_rates)
        two_qubits_error_rates_keys = self.two_qubits_error_rates.keys()
        qubits = []
        for key in two_qubits_error_rates_keys:
            key = key.split('_')
            for i in range(len(key)):
                key[i] = int(key[i])
        for i in range(0,len(self.two_qubits_error_rates)):
            t[i] = self.device_to_simulate.properties().gate_length(gate,key)

        return (np.mean(t)*(10**9))

    #---------------
    def add_all_noise_channels2(self):
        self.add_depolarizing_channel2()
        self.add_spam_channel2()
        self.add_relaxation_dephasing_channel2()

    def add_depolarizing_channel2(self):
        # add 1Q noise
        for qubit in self.qubits:
            error = depolarizing_error(self.single_qubit_error_rates[qubit], 1)
            self.noise_model.add_quantum_error(error,self.single_qubit_basis_gates,[qubit])

        keys = self.two_qubits_error_rates.keys()
        keys_used = {}
        # add 2Q noise
        for qubits_pair in keys:
            qubits = qubits_pair.split('_')
            inverse_qubits_pair = qubits[1] + '_' + qubits[0]

            if(qubits_pair in keys_used or inverse_qubits_pair in keys_used):
                continue
            
            keys_used[qubits_pair] = 1
            keys_used[inverse_qubits_pair] = 1
            
            aux_two_qubits_basis_gates = []
            for i in range(len(self.two_qubits_basis_gates)):
                if self.two_qubits_basis_gates[i] == 'ecr':
                    aux_two_qubits_basis_gates.append('cx')
                else:
                    aux_two_qubits_basis_gates[i].append(self.two_qubits_basis_gates[i])

            error = depolarizing_error(self.two_qubits_error_rates[qubits_pair], 2)
            self.noise_model.add_quantum_error(error,aux_two_qubits_basis_gates,[int(qubits[0]),int(qubits[1])])
    
    def add_spam_channel2(self):
        for qubit in self.qubits:
            error = pauli_error([("X", self.measurement_error_rates[qubit]), ("I", 1 - self.measurement_error_rates[qubit])])
            self.noise_model.add_quantum_error(error,"measure",[qubit])

    def add_relaxation_dephasing_channel2(self):
        # instructions times (in nanoseconds)
        avg_SQGateExecutionTime = []
        for gate in self.single_qubit_basis_gates:
            avg_SQGateExecutionTime.append(self._getSQGateExecutionTime(gate))
        avg_TQGateExecutionTime = []
        for gate in self.two_qubits_basis_gates:
            avg_TQGateExecutionTime.append(self._getTQGateExecutionTime(gate))
        time_reset = 1000  # 1 microsecond
        time_measure = 1000 # 1 microsecond

        # QuantumError objects
        errors_measure = [thermal_relaxation_error(t1, t2, time_measure)
                  for t1, t2 in zip(self.T1s, self.T2s)]
        errors_reset = [thermal_relaxation_error(t1, t2, time_reset)
                for t1, t2 in zip(self.T1s, self.T2s)]
        SQerrors = []
        for i in range(len(self.single_qubit_basis_gates)):
            SQerrors.append([thermal_relaxation_error(t1, t2, avg_SQGateExecutionTime[i])
              for t1, t2 in zip(self.T1s, self.T2s)])
        TQerrors = []
        for i in range(len(self.two_qubits_error_rates)):
            TQerrors.append([thermal_relaxation_error(t1, t2, avg_TQGateExecutionTime[0])
              for t1, t2 in zip(self.T1s, self.T2s)])


    #----------

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


    