# FabSCEMa

# How to run a SCEMa (test) Job

These examples assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have built and configured SCEMa (https://github.com/UCL-CCS/SCEMa) on the target machine.

Two minimal examples of  SCEMa simulation are provided in ``config_files/SCEMa_test1`` and  ``config_files/SCEMa_test2`` to execute these examples type:

``fabsim localhost SCEMa:SCEMa_test1``

``fabsim localhost SCEMa:SCEMa_test2``

# Run Ensemble Examples

### SCEMa_ensemble_example1

These examples assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have built and configured SCEMa (https://github.com/UCL-CCS/SCEMa) on the target machine.

To run type:
```
fabsim localhost SCEMa_ensemble:SCEMa_ensemble_example1
```
This example runs 3 simulations with different input files, which vary the simulation temperature, using the same topology file.


### SCEMa_ensemble_example2

This example runs 6 simulations with different input files, which vary the simulation timestep, using the same topology file.

To run type:
```
fabsim localhost  SCEMa_ensemble:SCEMa_ensemble_example2
```
