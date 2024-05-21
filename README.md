# QuantumQuipu_NoiseAndNativeGates
Repository of the "Noise and Native gates" research project of the Quantum Quipu group. The objectives of the project are:

* Study different noise simulation methods in superconducting qubits.
* Study different noise mitigation methods.
* Simulate noise in NISQ devices.
* Reproduce and expand the results presented with error mitigation methods.

----------------------------------------------------------------------------------------------------------------------------------

  Mentor: Victor Onofre.

  Quantum Interns: Adriano Lusso.

## Results

In branch 'qpl' you can find the latest results of this project. This includes:

* In codigo/project directory, an implementation of a unified noise model inspired by "Konstantinos Georgopoulos, Clive Emary, and Paolo Zuliani - Modeling and simulating the noisy behavior of near-term quantum computers".
* In conference_experiment, all the files related to and experiment which motivates a 3-page abstract and a poster that was accepted for QPL 2024 (https://qpl2024.dc.uba.ar/accepted.html).
* In Presentacion Escuela de computacion cuantica en español/, the slides and video presentation of light talk done for "Escuela de Computación cuántica en español", an event organized in terms of the Qiskit Fall Fest. This event aims to introduce spanish speakers into the world of quantum computing.



## DEV

Installation and usage of pre-commit:

Our code needs to have a minimum of coherence between its different pieces if we want to avoid troubles. Pre-commit applies a uniform style on everyting and will check for basic problems in the code. To install and use it, please follow these steps:

* pip install pre-commit
* or brew install pre-commit
* pre-commit install
* pre-commit run -a

It should then run each time you make a commit. When it fails, it sometimes auto-fixes the problems, mainly if they are style related. You then just need to add the changes and commit again. If they are not auto-fixed, fix them, add them and commit. When everything is green you can push !
