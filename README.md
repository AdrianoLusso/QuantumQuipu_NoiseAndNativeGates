# QuantumQuipu_NoiseAndNativeGates
Repositorio del proyecto de Investigación "Noise and Native Gates" del grupo Quantum Quipu. Los objetivo del proyecto son:

* Estudiar distintos métodos de siimulación de ruido en qubits superconductores.
* Estudiar distintos métodos de mitigación de ruido.
* Simular el ruido en NISQ devices.
* Reproducir y expandir los resultados presentados con metodos de mitigación de errores.

----------------------------------------------------------------------------------------------------------------------------------

  Mentor: Victor Onofre.

  Quantum Inters: Adriano Lusso, Maria Ramos.


## DEV

Installation and usage of pre-commit:

Our code needs to have a minimum of coherence between its different pieces if we want to avoid troubles. Pre-commit applies a uniform style on everyting and will check for basic problems in the code. To install and use it, please follow these steps:

* pip install pre-commit
* or brew install pre-commit
* pre-commit install
* pre-commit run -a

It should then run each time you make a commit. When it fails, it sometimes auto-fixes the problems, mainly if they are style related. You then just need to add the changes and commit again. If they are not auto-fixed, fix them, add them and commit. When everything is green you can push !
