from qiskit import QuantumRegister
from qiskit_aer.noise import (NoiseModel,depolarizing_error,thermal_relaxation_error,pauli_error)


class Unified_Noise_Model:
    
    def __init__(self):
        """
        Create and empty noise model.
        """
        self.noise_model = NoiseModel()
        
    def add_all_noise_channels(self,statePreparation_error_prob,measurement_error_prob,statePreparation_error_gate,
    depolarizing_prob,one_qubit_gates, one_qubit_gates_times, two_qubits_gates, two_qubits_gates_times, qubits, qubits_T1,qubits_T2):
        """
        Add the three noise channels to the UNM:
        1- Depolarizing Channel.
        2- SPAM Channel.
        3- Relaxation and Dephasing Channel.

        Args:
            statePreparation_error_prob(float): probability of error during the state preparation.
            measurement_error_prob(float): probability of error during measurement.
            statePreparation_error_gate(Gate): the X gate that will represent the noise after the state preparation.
            In your circuit, this gate must appear, in each qubit, after the state preparation.
            This gate must have a different label settled so as to this channel can works. It is recommended to label
            the gate as 'x_StatePreparation'.
        
            depolarizing_prob(float): probability of a depolarizing error to happen.

             qubits (QuantumRegister): Qubits of the circuit to which add noise.
            one_qubit_gates(string[]): list of strings representing one qubit gates with noise.
            one_qubit_gates_time(float[qubits][gates]): list of execution times for each (qubit,one qubit gate).
            two_qubits_gates(string[]):list of strings representing two qubits gates with noise.
            two_qubits_gates_time(float[qubits][gates]):list of execution times for each (qubit,two qubits gate).
            !!!TWO_QUBITS_GATES_TIME ESTA ACTUALMENTE SIMPLIFICADO, RECIBE UN FLOAT[]
             qubitsT1(float[]): list of floats that represents T1 for each of the qubits. 
            qubitsT2(float[]): list of floats that represents T2 for each of the qubits.
        """

        self.add_depolarizing_channel(self,depolarizing_prob,one_qubit_gates,two_qubits_gates)

        self.add_relaxation_dephasing_channel(qubits,qubits_T1,qubits_T2,one_qubit_gates,one_qubit_gates_times,
                                              two_qubits_gates,two_qubits_gates_times)
        
        self.add_spam_channel(statePreparation_error_prob,measurement_error_prob,statePreparation_error_gate)


    def add_spam_channel(self,statePreparation_error_prob=-1,measurement_error_prob=-1,statePreparation_error_gate=None):
        '''
        Add the SPAM channel to the UNM

        Args:
        statePreparation_error_prob(float): probability of error during the state preparation.
        measurement_error_prob(float): probability of error during measurement.
        statePreparation_error_gate(Gate): the X gate that will represent the noise after the state preparation.
        In your circuit, this gate must appear, in each qubit, after the state preparation.
        This gate must have a different label settled so as to this channel can works. It is recommended to label
        the gate as 'x_StatePreparation'.
        
        Considerations:
        the error probabilities are the same for each qubit. In future updates, it will be possible to set different
        statePreparation_error_prob and measurement_error_prob for each qubit.
        '''

        # state preparation errors
        if(statePreparation_error_prob >=0):
            statePreparation_error = pauli_error([('I',statePreparation_error_prob),('X',1-statePreparation_error_prob)])
            self.noise_model.add_all_qubit_quantum_error(statePreparation_error,statePreparation_error_gate.label)
            self.noise_model.add_basis_gates(['x'])

        if(measurement_error_prob >=0):
            measurement_error = pauli_error([('X',measurement_error_prob),('I',1-measurement_error_prob)])
            self.noise_model.add_all_qubit_quantum_error(measurement_error,"measure")
    
    

    def add_depolarizing_channel(self,depolarizing_prob,one_qubit_gates,two_qubits_gates,
                                 add_one_qubit_gates_noise = True, add_two_qubits_gates_noise=True):
        
        '''
        Create a depolarizing channel.
        
        Args:
            depolarizing_prob(float): probability of depolarizing error to happen
            one_qubit_gates(string[]): list of strings representing one qubit gates with noise
            two_qubits_gates(string[]):list of strings representing two qubits gates with noise.
            add_one_qubit_gates_noise(Boolean): defines if the channel will add noise to one qubit gates
            add_two_qubits_gates_noise(Boolean): defines if the channel will add noise to two qubits gates

        Considerations:
        the error probabilities are the same for each qubit,and for two qubits and one qubit gates. In future updates,
        it will be possible to set different probabilties for each qubit and amount of qubits.
        '''
        
        # Noise to one qubit gates
        if add_one_qubit_gates_noise:
            error = depolarizing_error(depolarizing_prob, 1)
            self.noise_model.add_all_qubit_quantum_error(error,one_qubit_gates)

        # Noise to two qubits gates
        if add_two_qubits_gates_noise:
            error = depolarizing_error(depolarizing_prob, 2)
            self.noise_model.add_all_qubit_quantum_error(error, two_qubits_gates)

    def add_relaxation_dephasing_channel(self,qubits:QuantumRegister,qubits_T1:list,qubits_T2:list,one_qubit_gates:list,
                 one_qubit_gates_times:list, two_qubits_gates:list = [], two_qubits_gates_times:list = []):
        
        """
        Creates a relaxation and dephasing channel.

        Args:
            qubits (QuantumRegister): Qubits of the circuit to which add noise.
            qubitsT1(float[]): list of floats that represents T1 for each of the qubits. 
            qubitsT2(float[]): list of floats that represents T2 for each of the qubits. 
            singleGates(string[]): list of strings representing single gates with noise.
            singleGatesTime(float[qubits][gates]): list of execution times for each (qubit,single gate).
            doubleGates(string[]):list of strings representing double gates with noise.
            doubleGatesTime(float[qubits][gates]):list of execution times for each (qubit,double gate).
            !!!DOUBLE_GATES_TIME ESTA ACTUALMENTE SIMPLIFICADO, RECIBE UN FLOAT[]
        """

        #For each qubit, we add it respective one_qubit and two_qubit gates noise
        for qubit in qubits:

            #Here, we add the one_qubit gates noise
            for gate in range(len(one_qubit_gates)):
                error = thermal_relaxation_error(qubits_T1[qubit],qubits_T2[qubit],one_qubit_gates_times[qubit][gate])
                self.noise_model.add_quantum_error(error,one_qubit_gates[gate],[qubit])

            #Here, we add the two_qubit gates noise
            for second_qubit in qubits:
                for gate in range(len(two_qubits_gates)):
                    error = thermal_relaxation_error(qubits_T1[qubit],qubits_T2[qubit],two_qubits_gates_times[gate]).expand(
                    thermal_relaxation_error(qubits_T1[second_qubit],qubits_T2[second_qubit],two_qubits_gates_times[gate]))
                    self.noise_model.add_quantum_error(error,two_qubits_gates[gate],[qubit,second_qubit])
