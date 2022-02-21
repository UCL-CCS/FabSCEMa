# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is
# distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabSCEMa.
# authors:
#           Kevin Bronik, Derek Groen, Maxime Vassaux,
#           and Werner Müller

try:
    from fabsim.base.fab import *
except ImportError:
    from fabsim.base import *

from pprint import pprint
import os
import yaml
import ruamel.yaml

# Add local script, blackbox and template path.
add_local_paths("FabSCEMa")

FabSCEMa_path = get_plugin_path('FabSCEMa')


@task
@load_plugin_env_vars("FabSCEMa")
def SCEMa(config, **args):
    """
    fabsim localhost SCEMa:SCEMa_test1
    """
    env.update(env.SCEMa_params)
    return SCEMa_job(config, 'SCEMa', **args)


def SCEMa_job(config, script, **args):
    """
    Submit an SCEMa job
    input args

        script:
            input script for job execution,
            available scripts : SCEMa
        config:
            config directory to use to define geometry
            please look at /FabSCEMa/config_files to see the available configs
    """
    update_environment(args)
    with_config(config)
    execute(put_configs, config)
    return job(dict(script=script,
                    memory='4G'),
               args)


@task
@load_plugin_env_vars("FabSCEMa")
def SCEMa_ensemble(config, sweep_dir=False, **kwargs):
    '''
        fabsim localhost SCEMa_ensemble:SCEMa_ensemble_example1

    '''
    env.update(env.SCEMa_params)
    SCEMa_ensemble_run(config, 'SCEMa', sweep_dir, **kwargs)



def SCEMa_ensemble_run(config, script, sweep_dir, **kwargs):

    # If sweep_dir not set assume it is a directory in config with default name
    if sweep_dir is False:
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, env.sweep_dir_name)

    env.script = script
    with_config(config)
    run_ensemble(config, sweep_dir, **kwargs)



@task
@load_plugin_env_vars("FabSCEMa")
def SCEMa_init_run_analyse_campaign_remote(config, **args):

    update_environment(args)
    with_config(config)
    # to prevent mixing with previous campaign runs
    env.prevent_results_overwrite = "delete"
    execute(put_configs, config)

    # adds a label to the generated job folder
    job_lable = 'init_run_analyse_campaign_remote'
    # job_name_template: ${config}_${machine_name}_${cores}
    env.job_name_template += '_{}'.format(job_lable)

    env.script = 'SCEMa_init_run_analyse_campaign_remote'
    job(args)

@task
@load_plugin_env_vars("FabSCEMa")
def SCEMa_init_run_analyse_campaign_local(config, **args):

    update_environment(args)
    with_config(config)
    # to prevent mixing with previous campaign runs
    env.prevent_results_overwrite = "delete"
    execute(put_configs, config)

    # adds a label to the generated job folder
    job_lable = 'init_run_analyse_campaign_local'
    # job_name_template: ${config}_${machine_name}_${cores}
    env.job_name_template += '_{}'.format(job_lable)

    env.script = 'SCEMa_init_run_analyse_campaign_local'
    job(args)
def get_FabSCEMa_tmp_path():
    """ Creates a directory within FabSCEMa for file manipulation
    Once simulations are completed, its contents can be removed"""
    tmp_path = FabSCEMa_path + "/tmp"
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)
    return tmp_path
