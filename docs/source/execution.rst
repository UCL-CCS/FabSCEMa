.. _execution:

This document briefly details how user/developers can set up a remote machine on FabSim3 for job submission.

How to run a SCEMa (test) Job
=======================

These examples assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have built and configured SCEMa (https://github.com/UCL-CCS/SCEMa) on the target machine.

All the input files required for a SCEMa simulation should be contained in a directory in ``config_files``.


Two minimal example Convection2D simulation is provided in ``config_files/SCEMa_test1`` and ``config_files/SCEMa_test2`` to execute these examples type:

    .. code-block:: console
		
		fabsim localhost SCEMa:SCEMa_test1
		fabsim localhost SCEMa:SCEMa_test2




Run Ensemble Examples
=====================

SCEMa_ensemble_example1
------------------------
This example will assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have built and configured SCEMa (https://github.com/UCL-CCS/SCEMa) on the target machine.

To run type:

    .. code-block:: console
		
		fabsim localhost SCEMa_ensemble:SCEMa_ensemble_example1
		
This example runs 3 simulations with different input files, which vary the simulation temperature, using the same topology file.


SCEMa_ensemble_example2
------------------------
This example will assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have built and configured SCEMa (https://github.com/UCL-CCS/SCEMa) on the target machine.

To run type:

    .. code-block:: console
		
		fabsim localhost  SCEMa_ensemble:SCEMa_ensemble_example2



This example runs 6 simulations with different input files, which vary the simulation timestep, using the same topology file.
		

EasyVVUQ+FabSCEMa
===================

These examples assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have built and configured SCEMa (https://github.com/UCL-CCS/SCEMa) on the target machine.

.. Note:: All the easyvvuq campaign runs and  execution, and the results analyse will be done on target machine which can be your localhost or remote HPC machine.

The input files needed for this example are found in ``plugins/FabSCEMa/config_files/fabSCEMa_easyvvuq_InRuAn*_QCGPJ``. This directory contains the following files that can be modified for your own purpose:


* ``SCEMa_remote.template``: is the convection2d input script in ``fabSCEMa_easyvvuq_InRuAn*_QCGPJ`` subfolder, EasyVVUQ will substitute certain variables in this file to create the ensemble.

* ``campaign_params_remote.yml``: is the configuration file, in ``fabSCEMa_easyvvuq_InRuAn*_QCGPJ`` subfolder, for EasyVVUQ sampler. If you need different sampler, parameter to be varied, or polynomial order, you can set them in this file.

Execution
---------
After updating the following files with your credentials

    .. code-block:: console
		
		FabSim3/deploy/machines_user.yml
		FabSim3/deploy/machines.yml
		FabSim3/plugins/FabNEPTUNE/machines_FabNEPTUNE_user.yml

``<remote machine>`` can be your ``localhost`` or a HPC resources.

To run type:

    .. code-block:: console
		
               fabsim   localhost   SCEMa_init_run_analyse_campaign_local:fabSCEMa_easyvvuq_InRuAn1_QCGPJ
               fabsim   <remote machine name>   SCEMa_init_run_analyse_campaign_remote:fabSCEMa_easyvvuq_InRuAn1_QCGPJ
	       
To copy the results back to your local machine type:

    .. code-block:: console	       
	       
	       fabsim  localhost   fetch_results
	       fabsim  <remote machine name>   fetch_results
	       
	      
EasyVVUQ+EasySurrogate+FabSCEMa
=================================

These examples assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have built and configured SCEMa (https://github.com/UCL-CCS/SCEMa) on the target machine.

.. Note:: All the EasyVVUQ and EasySurrogate campaigns runs and execution, and the results analyse will be done on target machine which can be your localhost or remote HPC machine.


The input files needed for this example are found in ``plugins/FabSCEMa/config_files/fabSCEMa_easyvvuq_easysurrogate_InRuAn*_DAS_QCGPJ``. This directory contains the following files that can be modified for your own purpose:


* ``SCEMa_remote.template``: is the convection2d input script in ``fabSCEMa_easyvvuq_easysurrogate_InRuAn*_DAS_QCGPJ`` subfolder, EasyVVUQ will substitute certain variables in this file to create the ensemble.

* ``campaign_params_remote.yml``: is the configuration file, in ``fabSCEMa_easyvvuq_easysurrogate_InRuAn*_DAS_QCGPJ`` subfolder, for EasyVVUQ sampler. If you need different sampler, parameter to be varied, or polynomial order, you can set them in this file.

Execution
---------
After updating the following files with your credentials

    .. code-block:: console
		
		FabSim3/deploy/machines_user.yml
		FabSim3/deploy/machines.yml
		FabSim3/plugins/FabNEPTUNE/machines_FabNEPTUNE_user.yml

``<remote machine>`` can be your ``localhost`` or a HPC resources.

To run type:

    .. code-block:: console
		
               fabsim   localhost   SCEMa_init_run_analyse_campaign_local:fabSCEMa_easyvvuq_easysurrogate_InRuAn1_DAS_QCGPJ
               fabsim   <remote machine name>   SCEMa_init_run_analyse_campaign_remote:fabSCEMa_easyvvuq_easysurrogate_InRuAn1_DAS_QCGPJ
	       fabsim   localhost   SCEMa_init_run_analyse_campaign_local:fabSCEMa_easyvvuq_easysurrogate_InRuAn2_DAS_QCGPJ
	       fabsim   <remote machine name>   SCEMa_init_run_analyse_campaign_remote:fabSCEMa_easyvvuq_easysurrogate_InRuAn2_DAS_QCGPJ
	       
To copy the results back to your local machine type:

    .. code-block:: console	       
	       
	       fabsim  localhost   fetch_results
	       fabsim  <remote machine name>   fetch_results
	       


