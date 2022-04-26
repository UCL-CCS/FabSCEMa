.. _workflow:


FabSCEMa Workflow
==============

Introduction
------------
The FabSCEMa tool in combination with an existing platform for verification, validation, and uncertainty quantification offers a scientific simulation environment and data processing workflows that enable the execution of single and ensemble simulations. This Fabsim-plugin also supports the execution of remotely or locally submitted jobs through the plugin and helps the experts to do several specific annalistic tasks on a local machine or on a cluster or supercomputing platform within the EasyVVUQ and EasySurrogate architectures. It is a fully automated computational tool for the study of the uncertainty in a computational model of a heterogeneous multi-scale atomistic continuum coupling system, a publicly available open-source code SCEMa (https://GitHub.com/UCL-CCS/SCEMa).


Example of workflow for FabSCEMa
------------------------------------------------------------------
An already implemented example from FabSCEMa's project will be explained in the following. 

SCEMa (Simulation Coupling Environment for Materials)
-----------------------------------------------------
Mechanisms emerging across multiple scales are ubiquitous in physics and methods designed to investigate them are becoming essential. The heterogeneous multiscale method (HMM) is one of these, concurrently simulating the different scales while keeping them separate. Due to the significant computational expense, developments of HMM remain mostly theoretical and applications to physical problems are scarce. However, HMM is highly scalable and is well suited for high performance computing. With the wide availability of multi-petaflop infrastructures, HMM applications are becoming practical. Rare applications to mechanics of materials at low loading amplitudes exist, but are generally confined to the elastic regime. Beyond that, where history-dependent, irreversible or non-linear mechanisms occur, not only computational cost, but also data management issues arise. The microscale description loses generality, developing a specific microstructure based on the deformation history, which implies inter alia that as many microscopic models as discrete locations in the macroscopic description must be simulated and stored. Here we present a detailed description of the application of HMM to inelastic mechanics of materials, with emphasis on the efficiency and accuracy of the scale bridging methodology. The method is well-suited to the estimation of macroscopic properties of polymers (and derived nanocomposites) starting from knowledge of their atomistic chemical structure. Through application of the resulting workflow to polymer fracture mechanics, we demonstrate deviation in the predicted fracture toughness relative to a single scale molecular dynamics approach, thus illustrating the need for such concurrent multiscale methods in the predictive estimation of
macroscopic properties.

.. image:: ../../images/scema.png
   :align: center
   :class: with-shadow
   :scale: 50

References
    .. code-block:: console
		
		Vassaux, M., Richardson, R. A., & Coveney, P. V. (2019). The heterogeneous multiscale method applied to inelastic polymer mechanics. Philosophical Transactions of the Royal Society A, 377(2142), 20180150.
    
    
Submitting  job
------------------------------------------------------------------

Before submitting the simulation to a remote machine, two YAML files must be edited. First we need to modify the file

      .. code-block:: yaml
      
           FabSim3/deploy/machines_user.yml 

and add the login credentials in the template so that FabNEPTUNE knows where to run the simulation. 
The following example shows what parameters (username, project, budget and sshpass) need to be defined for a remote machine name ARCHER2 (the UK National Supercomputer). Other machines may have more or less parameters that need to be defined.

	.. code-block:: yaml
	
                  archer2:		
                         username: "<your-username>"
                         project: "e123"
                         budget: "e123-user"
                         sshpass: "<ARCHER2-password>"
                         manual_sshpass: true



The next important file that needs to be updated is 

        .. code-block:: yaml
	
              FabSim3/plugins/FabNEPTUNE/machines_FabNEPTUNE_user.yml 

In this file you can set the path to the convection2d/3d executable on the remote machine which are Nektar++ executable and the input file names, and the remote run command. Here we assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have configured and built Nektar++ (https://www.nektar.info/) on the target machine, and successfully tested the executable code!. However, most HPC clusters could have Nektar++ available as a module and this can be added in the loaded modules section of the file. This means that the ``convection2d_exec`` parameter can be set to the path of the compiled executable. For example, archer2 remote machine might look like:

	.. code-block:: yaml

		archer2:
		   convection2d_exec: ".../nektar++/build/dist/bin/IncNavierStokesSolver"
		   ...
		   FabNEPTUNE_params:
                         convection_2d_input: "convection_2d.xml"
                         convection_3d_input: "convection_3d.xml"
                         sweep_dir_name: "SWEEP"

                   ...
                   run_command_remote: "srun --nodes=1 --ntasks=1 --exclusive --oversubscribe --mem=25000M"
		   ...
		   ...
		   ...
		   modules:
		      loaded: ["python"]

After all the above configurations done we still would need to update ``FabSim3/fabsim/deploy/templates``. For example, the template (slurm-archer2) for archer2 remote machine might look like:

           .. code-block:: bash
	   
	         #!/bin/bash
                 ## slurm-archer2
                 ## number of nodes
                 #SBATCH --nodes 70

                 ## SBATCH --nodes $nodes
                 #SBATCH --ntasks=8960
                 ## task per node
                 #SBATCH --tasks-per-node=$corespernode
                 #SBATCH --cpus-per-task=1
                 ## wall time in format MINUTES:SECONDS
                 #SBATCH --time=$job_wall_time


                 ## grant
                 #SBATCH --account=$budget

                 ## stdout file
                 #SBATCH --output=$job_results/JobID-%j.output

                 ## stderr file
                 #SBATCH --error=$job_results/JobID-%j.error

                 #SBATCH --partition=$partition_name
                 #SBATCH --qos=$qos_name

                 export OMP_NUM_THREADS=1
                 export FI_MR_CACHE_MAX_COUNT=0
                 export PATH="/mnt/lustre/a2fs-work2/work/e723/e723/kevinb/miniconda3/bin:$PATH"
                 export PATH="/mnt/lustre/a2fs-work2/work/e723/e723/kevinb/.local/.local/bin:$PATH"
                 export NEK_DIR=/mnt/lustre/a2fs-work2/work/e723/e723/kevinb/nektarpp/build
                 export NEK_BUILD=$NEK_DIR/dist/bin
                 export LD_LIBRARY_PATH=/opt/gcc/10.2.0/snos/lib64:$NEK_DIR/ThirdParty/dist/lib:$NEK_DIR/dist/lib64:$LD_LIBRARY_PATH
                 export PATH="/mnt/lustre/a2fs-work2/work/e723/e723/kevinb/nektarpp/build/dist/bin:$PATH"

Once all have been done, we can submit a simulation to a remote machine using the command:

    .. code-block:: console
		
		fabsim archer2 Convection2D_remote:convection_2d_test	

and copy the results back to our local machine with

    .. code-block:: console
		
		fabsim  archer2  fetch_results
		
		
Practical Illustration
==============	

In the following we will provide a step-by-step demonstration of how to perform a job submission and also we will demonstrate the output of analysis.

step one
--------

Specific set of tasks required before submitting the job onto the remote/local machine. Two input files that are found in:

      .. code-block:: console
             
	     plugins/FabNEPTUNE/config_files/convection_2d_easyvvuq_easysurrogate_InRuAn*_DAS_QCGPJ 

are the most important files which can be modified for your own specific purpose.

``convection_2d_remote.template`` file:
---------------------------------------
 
    .. code-block:: console
		
		[convection_2d_remote.template] It is the convection2d input script in convection_2d_easyvvuq_easysurrogate_InRuAn*_DAS_QCGPJ subfolder, EasyVVUQ will substitute certain variables in this file to create the ensemble
 
Here, as shown in the following, Rayleigh, Prandtl, Temperature  and Diffusion Coefficient are selected as model inputs for Variance-based sensitivity analysis (Sobol method)

A working example:


           .. code-block:: bash
	   
	         <?xml version="1.0" encoding="utf-8" ?>
		 <NEKTAR>
                 <EXPANSIONS>
                    <E COMPOSITE="C[0]" NUMMODES="4" FIELDS="u,v,T,p" TYPE="GLL_LAGRANGE_SEM" />
                 </EXPANSIONS>
                 <CONDITIONS>
                      <SOLVERINFO>
                         <I PROPERTY="SOLVERTYPE"              VALUE="VCSWeakPressure"         />
                         <I PROPERTY="EQTYPE"                  VALUE="UnsteadyNavierStokes"    />
                         <I PROPERTY="Projection"              VALUE="Continuous"              />
                         <I PROPERTY="EvolutionOperator"       VALUE="Nonlinear"               />
                         <I PROPERTY="TimeIntegrationMethod"   VALUE="IMEXOrder2"              />
                         <I PROPERTY="Driver"                  VALUE="Standard"                />
                         <I PROPERTY="SpectralVanishingViscosity" VALUE="True"                 />
                         <I PROPERTY="SpectralHPDealiasing"       VALUE="True"                 />
                      </SOLVERINFO>
                      <VARIABLES>
                         <V ID="0"> u </V>
                         <V ID="1"> v </V>
                         <V ID="2"> T </V>
                         <V ID="3"> p </V>
                      </VARIABLES>
                      <GLOBALSYSSOLNINFO>
                        <V VAR="u,v,T,p">
                           <I PROPERTY="IterativeSolverTolerance"  VALUE="1e-6"/>
                        </V>
                      </GLOBALSYSSOLNINFO>
                     <PARAMETERS>
                        <P> TimeStep        = 0.0000001            </P>
                        <P> T_Final         = 0.0001               </P>
                        <P> NumSteps        = T_Final/TimeStep     </P>
                        <P> IO_infoSteps    = 10                   </P>
                        <P> Ra              = ${Rayleigh}E2        </P>
                        <P> Pr              = ${Prandtl}           </P>
                        <P> Kinvis          = Pr                   </P>
                    </PARAMETERS>
                    <BOUNDARYREGIONS>
                       <B ID="0"> C[1] </B>
                       <B ID="1"> C[2] </B>
                       <B ID="2"> C[3] </B>
                       <B ID="3"> C[4] </B>
                    </BOUNDARYREGIONS>
                    <BOUNDARYCONDITIONS>
                      <REGION REF="0">
                        <D VAR="u" VALUE="0" />
                        <D VAR="v" VALUE="0" />
                        <N VAR="T" VALUE="0" />
                        <N VAR="p" USERDEFINEDTYPE="H" VALUE="0" />
                     </REGION>
                     <REGION REF="1"> <!-- top (insulated) -->
                        <D VAR="u" VALUE="0" />
                        <D VAR="v" VALUE="0" />
                        <N VAR="T" VALUE="0" />
                        <N VAR="p" USERDEFINEDTYPE="H" VALUE="0" />
                     </REGION>
                     <REGION REF="2">
                       <D VAR="u" VALUE="0" />
                       <D VAR="v" VALUE="0" />
                       <D VAR="T" VALUE="${Temperature}" />
                       <N VAR="p" USERDEFINEDTYPE="H" VALUE="0" />
                     </REGION>
                     <REGION REF="3">
                       <D VAR="u" VALUE="0" />
                       <D VAR="v" VALUE="0" />
                       <D VAR="T" VALUE="0" />
                       <N VAR="p" USERDEFINEDTYPE="H" VALUE="0" />
                     </REGION>
                     </BOUNDARYCONDITIONS>
                     <FUNCTION NAME="InitialConditions">
                       <E VAR="u" VALUE="0" />
                       <E VAR="v" VALUE="0" />
                       <E VAR="T" VALUE="1-x" />
                       <E VAR="p" VALUE="0" />
                     </FUNCTION>
                     <FUNCTION NAME="BodyForce">
                       <E VAR="u" VALUE="0" EVARS="u v T p" />
                       <E VAR="v" VALUE="Ra*Pr*T" EVARS="u v T p" />
                       <E VAR="T" VALUE="0" EVARS="u v T p"  />
                     </FUNCTION>
                     <FUNCTION NAME="DiffusionCoefficient">
                       <E VAR="T" VALUE="${DiffusionCoefficient}" />
                     </FUNCTION>
                 </CONDITIONS>		
                 <FORCING>
                    <FORCE TYPE="Body">
                    <BODYFORCE> BodyForce </BODYFORCE>
                 </FORCE>
                 </FORCING>
                 <FILTERS>
                   <FILTER TYPE="AeroForces">
                     <PARAM NAME="OutputFile"> NusseltTest1L  </PARAM>
                     <PARAM NAME="OutputFrequency"> 10        </PARAM>
                     <PARAM NAME="Boundary"> B[2]             </PARAM>
                   </FILTER>
                   <FILTER TYPE="AeroForces">
                     <PARAM NAME="OutputFile"> NusseltTest1R  </PARAM>
                     <PARAM NAME="OutputFrequency"> 10        </PARAM>
                     <PARAM NAME="Boundary"> B[3]             </PARAM>
                   </FILTER>
                   <FILTER TYPE="HistoryPoints">
                     <PARAM NAME="OutputFile"> PointTest      </PARAM>
                     <PARAM NAME="OutputFrequency"> 10        </PARAM>
                     <PARAM NAME="Points"> 0.5 1.0 0.0        </PARAM>
                   </FILTER>
	           <FILTER TYPE="AverageFields">
    	             <PARAM NAME="OutputFile"> AveragedTest   </PARAM>
                     <PARAM NAME="SampleFrequency"> 10        </PARAM>
	           </FILTER>
                 </FILTERS>
                 </NEKTAR>


Visual explanation of the concept
---------------------------------

.. image:: ../../images/minx.png
   :alt: modelinputs
   :class: with-shadow
   :scale: 40
   
``campaign_params_remote.yml`` file:
------------------------------------

    .. code-block:: console
		
		[campaign_params_remote.yml] It is the configuration file, in convection_2d_easyvvuq_easysurrogate_InRuAn*_DAS_QCGPJ subfolder, for EasyVVUQ sampler. If you need different sampler, parameter to be varied, or polynomial order, you can set them in this file
		
Here, as shown in the following, F1-press_L, F1-visc_L, F1-pres_R and F1-visc_R are selected as model outputs for Variance-based sensitivity analysis (Sobol method)

A working Example:

	.. code-block:: yaml

		parameters:
                           # <parameter_name:>
                           #   uniform_range: [<lower value>,<upper value>] 
                           Rayleigh:
                                   uniform_range: [0.5, 20000]
                           Prandtl:
                                   uniform_range: [5, 8.0]
                           DiffusionCoefficient:
                                   uniform_range: [0.5, 2.0]
                           Temperature:
                                   uniform_range: [1.5, 80.0]

                selected_parameters: ["Rayleigh",  'Prandtl', 'DiffusionCoefficient', 'Temperature']

                polynomial_order: 3

                campaign_name: "FabNEPTUNE"

                sub_campaign_name: "FabNEPTUNE_surrogate"

                encoder_delimiter: "@"

                encoder_template_fname : "convection_2d_remote.template"
                encoder_target_filename: "convection_2d.xml"
                decoder_target_filename: "output.csv"

                decoder_output_columns: ['F1-press_L', 'F1-visc_L', 'F1-pres_R', 'F1-visc_R']

                params:
                  Rayleigh:
                     type: "float"
                     min: "0.0"
                     max: "21000"
                     default: "1.0"

                  Prandtl:
                     type: "float"
                     min: "0.0"
                     max: "8.5"
                     default: "7.0"

                  DiffusionCoefficient:
                     type: "float"
                     min: "0.0"
                     max: "2.5"
                     default: "1.0"

                 Temperature:
                    type: "float"
                    min: "0.0"
                    max: "81.5"
                    default: "1.0"


                sampler_name: "PCESampler"
                distribution_type: "Uniform" # Uniform, DiscreteUniform
                quadrature_rule: "G"
                sparse: False
                growth: False
                midpoint_level1: False
                dimension_adaptive: False


Visual explanation of the concept
---------------------------------

.. image:: ../../images/cov_2d_output.png
   :alt: modeloutputs
   :class: with-shadow
   :scale: 40
   
step two
-------- 

Submit a simulation to a remote/local machine using the command:

    .. code-block:: console
		
		fabsim archer2 Convection2D_init_run_analyse_campaign_remote:convection_2d_easyvvuq_easysurrogate_InRuAn1_DAS_QCGPJ
		



You can check anytime the progress of simulation by looking at the error file (JobID-%j.error)


.. image:: ../../images/err.png
   :alt: err_ss
   :class: with-shadow
   :scale: 40	
   
   
step three
---------- 

Copy the results back to you local machine with

    .. code-block:: console
		
		fabsim  archer2  fetch_results
	
		
step four
----------

Result of the analysis of EasySurrogate+EasyVVUQ+FabNEPTUNE simulation, based on Sobol method and a surrogate method (Deep Active Subspace
), are shown in the following examples [Rayleigh, Prandtl, Temperature and Diffusion Coefficient as model inputs and F1-press_L, F1-visc_L, F1-pres_R and F1-visc_R as model outputs]:

Visual explanation of the surrogate method
------------------------------------------

.. image:: ../../images/surrogate.png
   :alt: surmodel
   :class: with-shadow
   :scale: 40
   
   
Analysis results
----------------  

.. image:: ../../images/ssm.png
   :alt: model_ss
   :class: with-shadow
   :scale: 40
   
.. image:: ../../images/sm.png
   :alt: mode_s
   :class: with-shadow
   :scale: 40 
   

   
.. Note:: If you wish to modify the model inputs/outputs and then run the simulation, there are several options for doing this. It can be easily done by modification of the following python files (in convection_2d_easyvvuq_easysurrogate_InRuAn*_DAS_QCGPJ subfolder):
    
                convection_2d_easyvvuq_init_run_analyse_remote.py 
                easyvvuq_convection_2d_RUN_remote.py  
