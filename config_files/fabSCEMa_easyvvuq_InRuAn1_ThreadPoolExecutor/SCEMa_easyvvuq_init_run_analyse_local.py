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
import os
import yaml
# import ruamel.yaml
# from pprint import pprint
from shutil import rmtree
# import json
import chaospy as cp
import numpy as np
# import tempfile
import easyvvuq as uq
import time
import pickle
import matplotlib
if not os.getenv("DISPLAY"):
    matplotlib.use("Agg")
import matplotlib.pylab as plt

import sys


def init_run_analyse_campaign(work_dir=None, sampler_inputs_dir=None , inpt=None):

    print('inpt', inpt)
    # from shlex import quote

    machine_name = inpt[0]
    run_command = inpt[1]
    SCEMa_exec = inpt[2]


    campaign_params = load_campaign_params(sampler_inputs_dir=sampler_inputs_dir, machine=machine_name)
    keys = list(campaign_params.keys())
    CRED = '\33[31m'
    CEND = '\33[0m'
    print('Campaign parameters <---------->')
    for key in keys:
        print(CRED + key, ':' + CEND, campaign_params[key])
    print('\x1b[6;30;45m' + '                   ' + '\x1b[0m')
    campaign_work_dir = os.path.join(
        work_dir,
        'SCEMa_easyvvuq_%s' % (campaign_params['sampler_name'])
    )
    if os.path.exists(campaign_work_dir):
        rmtree(campaign_work_dir)
    os.mkdir(campaign_work_dir)

    db_location = "sqlite:///" + campaign_work_dir + "/campaign.db"

    campaign = uq.Campaign(name=campaign_params['campaign_name'], db_location=db_location,
                           work_dir=campaign_work_dir)

    # Create an encoder and decoder
    encoder = uq.encoders.GenericEncoder(
        template_fname=os.path.join(sampler_inputs_dir, campaign_params[
                                    'encoder_template_fname']),
        delimiter=campaign_params['encoder_delimiter'],
        target_filename=campaign_params['encoder_target_filename']
    )

    decoder = uq.decoders.SimpleCSV(
        target_filename=campaign_params['decoder_target_filename'],
        output_columns=campaign_params['decoder_output_columns']
    )
    host = 'localhost'

    this_path = campaign._campaign_dir

    print('machine name:', CRED + str(machine_name) + CEND)
    print('run command:', CRED + str(run_command) + CEND)
    print('SCEMa_exec:', CRED + str(SCEMa_exec) + CEND)
    print('work_dir:', CRED + str(os.getcwd()) + CEND)

    # if str(machine_name) == 'localhost':
    #     print("Running locally")
    #     from dask.distributed import Client
    # else:
    #     print("Running using SLURM")
    #     from dask.distributed import Client
    #     from dask_jobqueue import SLURMCluster

    if str(machine_name) == 'localhost':
        print('\x1b[6;30;45m' + '.........................' + '\x1b[0m')
        print('\x1b[6;30;45m' + 'running on local machine!' + '\x1b[0m')
        print('\x1b[6;30;45m' + '.........................' + '\x1b[0m')
        execute = uq.actions.ExecuteLocal(
            'python3 {}/easyvvuq_SCEMa_RUN_localhost.py {} {} {}'.format(os.getcwd(),
            campaign_params['encoder_target_filename'], this_path, inpt))

    else:
        print('\x1b[6;30;45m' + '..........................' + '\x1b[0m')
        print('\x1b[6;30;45m' + 'running on remote machine!' + '\x1b[0m')
        print('\x1b[6;30;45m' + '..........................' + '\x1b[0m')
        execute = uq.actions.ExecuteLocal(
            'python3 {}/easyvvuq_SCEMa_RUN_remote.py {} {} {}'.format(os.getcwd(),
            campaign_params['encoder_target_filename'], this_path, inpt))

    actions = uq.actions.Actions(
        uq.actions.CreateRunDirectory(root=campaign_work_dir, flatten=True),
        uq.actions.Encode(encoder),
        execute,
        uq.actions.Decode(decoder))


    print('campaign_params[params]', campaign_params['params'])
    campaign.add_app(
        name=campaign_params['campaign_name'],
        params=campaign_params['params'],
        actions=actions
    )

    vary = {}
    for param in campaign_params['selected_parameters']:
        lower_value = campaign_params['parameters'][param]['uniform_range'][0]
        upper_value = campaign_params['parameters'][param]['uniform_range'][1]
        if campaign_params['distribution_type'] == 'DiscreteUniform':
            vary.update({param: cp.DiscreteUniform(lower_value, upper_value)})
        elif campaign_params['distribution_type'] == 'Uniform':
            vary.update({param: cp.Uniform(lower_value, upper_value)})
    # vary = {
    #     "strain rate": cp.Uniform(0.00001, 0.001),
    # }
    # # create SCSampler
    print('vary', vary)
    if campaign_params['sampler_name'] == 'SCSampler':
        sampler = uq.sampling.SCSampler(
            vary=vary,
            polynomial_order=campaign_params['polynomial_order'],
            quadrature_rule=campaign_params['quadrature_rule'],
            growth=campaign_params['growth'],
            sparse=campaign_params['sparse'],
            midpoint_level1=campaign_params['midpoint_level1'],
            dimension_adaptive=campaign_params['dimension_adaptive']
        )
    elif campaign_params['sampler_name'] == 'PCESampler':
        sampler = uq.sampling.PCESampler(
            vary=vary,
            polynomial_order=campaign_params['polynomial_order'],
            rule=campaign_params['quadrature_rule'],
            sparse=campaign_params['sparse'],
            growth=campaign_params['growth']
        )
    elif campaign_params['sampler_name'] == 'QMCSampler':
        sampler = uq.sampling.QMCSampler(
            vary=vary,
            n_mc_samples=32,
            count=2
        )
    elif campaign_params['sampler_name'] == 'RandomSampler':
        sampler = uq.sampling.RandomSampler(
            vary=vary
        )



    # Associate the sampler with the campaign
    # sampler=uq.sampling.MCSampler(vary=vary, n_mc_samples=16)
    campaign.set_sampler(sampler)
    time_start = time.time()
    campaign.draw_samples()
    print("Number of samples = %s" % campaign.get_active_sampler().count)
    #
    time_end = time.time()
    # from dask.distributed import Client
    # client = Client(processes=True, threads_per_worker=1)
    print("Time for phase 2 = %.3f" % (time_end - time_start))
    time_start = time.time()
    campaign.execute(pool=None).collate()


    time_end = time.time()
    print("Time for phase 3 = %.3f" % (time_end - time_start))
    time_start = time.time()
    time_end = time.time()
    print("Time for phase 4 = %.3f" % (time_end - time_start))
    time_start = time.time()
    output_column = campaign_params['decoder_output_columns']
    if campaign_params['sampler_name'] == 'SCSampler':
        analysis = uq.analysis.SCAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["resulting_force"]
        )
    elif campaign_params['sampler_name'] == 'PCESampler':
        analysis = uq.analysis.PCEAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["resulting_force"]
        )
    elif campaign_params['sampler_name'] == 'QMCSampler':
        analysis = uq.analysis.QMCAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["resulting_force"]
        )

    # ["index", "stress_00_macro", "stress_01_macro", "stress_02_macro", "stress_11_macro", "stress_12_macro",
    #  "stress_22_macro", "stress_00_nano", "stress_01_nano", "stress_02_nano", "stress_11_nano", "stress_12_nano",
    #  "stress_22_nano"]
    else:
        print("uq.analysis for sampler_name = %s is not specified! " %
              (campaign_params['sampler_name']))
        exit(1)
    time_end = time.time()
    print("Time for phase 5 = %.3f" % (time_end - time_start))

    campaign.apply_analysis(analysis)
    time_end = time.time()
    print("Time for phase 6 = %.3f" % (time_end - time_start))
    time_start = time.time()

    # Get Descriptive Statistics
    results_df = campaign.get_collation_result()
    results = campaign.get_last_analysis()


    print("descriptive statistics :")
    print(results.describe("resulting_force"))
    print("the first order sobol index :")
    print(results.sobols_first()['resulting_force'])

    mean = results.describe("resulting_force", "mean")
    var = results.describe("resulting_force", "var")

    t = np.linspace(0, 200, 150)
    results.plot_moments(qoi="resulting_force", ylabel="resulting_force", xlabel="Time", alpha=0.2,
                         filename=os.path.join(campaign_work_dir, 'resulting_force_moments.png'))
    results.plot_sobols_first(
        qoi="resulting_force", xlabel="Time",
        filename=os.path.join(campaign_work_dir, 'resulting_force_sobols_first.png')
    )

    plt.figure()
    rho00 = results.describe('resulting_force', 'mean')
    for k in results.sobols_total()['resulting_force'].keys():
        plt.plot(rho00, results.sobols_total()['resulting_force'][k], label=k)
    plt.legend(loc=0)
    plt.xlabel('resulting_force [N]')
    plt.ylabel('sobols_total')
    plt.title('resulting_force')
    plt.savefig(os.path.join(campaign_work_dir, 'resulting_force_sobols_total.png'))
    print("saving resulting_force_sobols_total.png -->", os.path.join(campaign_work_dir, 'resulting_force_sobols_total.png'))
    plt.close()
    plt.figure()
    rho02 = results.describe('resulting_force', 'mean')
    for k1 in results.sobols_second()['resulting_force'].keys():
        for k2 in results.sobols_second()['resulting_force'][k1].keys():
            plt.plot(rho02, results.sobols_second()['resulting_force'][k1][k2], label=k1 + '/' + k2)
    plt.legend(loc=0, ncol=2)
    plt.xlabel('resulting_force [N]')
    plt.ylabel('sobols_second')
    plt.title('resulting_force')
    plt.savefig(os.path.join(campaign_work_dir, 'resulting_force_sobols_second.png'))
    print("saving resulting_force_sobols_second.png -->",
          os.path.join(campaign_work_dir, 'resulting_force_sobols_second.png'))
    plt.close()
    #
    # t = np.linspace(0, 200, 150)
    # results.plot_moments(qoi="stress_00_nano", ylabel="stress_00_nano", xlabel="Time", alpha=0.2,
    #                      filename=os.path.join(campaign_work_dir, 'stress_00_nano_moments.png'))
    # results.plot_sobols_first(
    #     qoi="stress_00_nano", xlabel="Time",
    #     filename=os.path.join(campaign_work_dir, 'stress_00_nano_sobols_first.png')
    # )
    # plt.figure()
    # rho11 = results.describe('stress_00_nano', 'mean')
    # for k in results.sobols_total()['stress_00_nano'].keys():
    #     plt.plot(rho11, results.sobols_total()['stress_00_nano'][k], label=k)
    # plt.legend(loc=0)
    # plt.xlabel('stress_00_nano [Pa]')
    # plt.ylabel('sobols_total')
    # plt.title('stress_00_nano')
    # plt.savefig(os.path.join(campaign_work_dir, 'stress_00_nano_sobols_total.png'))
    # print("saving stress_00_nano_sobols_total.png -->",
    #       os.path.join(campaign_work_dir, 'stress_00_nano_sobols_total.png'))
    # plt.close()
    # plt.figure()
    # rho12 = results.describe('stress_00_nano', 'mean')
    # for k1 in results.sobols_second()['stress_00_nano'].keys():
    #     for k2 in results.sobols_second()['stress_00_nano'][k1].keys():
    #         plt.plot(rho12, results.sobols_second()['stress_00_nano'][k1][k2], label=k1 + '/' + k2)
    # plt.legend(loc=0, ncol=2)
    # plt.xlabel('stress_00_nano [Pa]')
    # plt.ylabel('sobols_second')
    # plt.title('stress_00_nano')
    # plt.savefig(os.path.join(campaign_work_dir, 'stress_00_nano_sobols_second.png'))
    # print("saving stress_00_nano_sobols_second.png -->",
    #       os.path.join(campaign_work_dir, 'stress_00_nano_sobols_second.png'))
    # plt.close()

    # stress_00_macro = results.describe("stress_00_macro", "mean")
    # # stress_01_macro = results.describe("stress_01_macro", "mean")
    # # stress_02_macro = results.describe("stress_02_macro", "mean")
    # # stress_11_macro = results.describe("stress_11_macro", "mean")
    # # stress_12_macro = results.describe("stress_12_macro", "mean")
    # # stress_22_macro = results.describe("stress_22_macro", "mean")
    #
    # stress_00_nano = results.describe("stress_00_nano", "mean")
    # # stress_01_nano = results.describe("stress_01_nano", "mean")
    # # stress_02_nano = results.describe("stress_02_nano", "mean")
    # # stress_11_nano = results.describe("stress_11_nano", "mean")
    # # stress_12_nano = results.describe("stress_12_nano", "mean")
    # # stress_22_nano = results.describe("stress_22_nano", "mean")



    time_end = time.time()
    print("Time for phase 7 = %.3f" % (time_end - time_start))
    time_start = time.time()

    pickle_file = os.path.join(campaign_work_dir, "SCEMa.pickle")
    with open(pickle_file, "bw") as f_pickle:
        pickle.dump(results, f_pickle)

    time_end = time.time()
    print("Time for phase 8 = %.3f" % (time_end - time_start))

    # plt.ion()
    #
    # # plot the calculated Te: mean, with std deviation, 10 and 90% and range
    # stress_00_macro_mean = results.describe("stress_00_macro", "mean")
    # stress_00_macro_std = results.describe("stress_00_macro", "std")
    # stress_00_macro_10_pct = results.describe("stress_00_macro", "10%")
    # stress_00_macro_90_pct = results.describe("stress_00_macro", "90%")
    # stress_00_macro_min = results.describe("stress_00_macro", "min")
    # stress_00_macro_max = results.describe("stress_00_macro", "max")
    #
    # plt.figure()
    # plt.plot(stress_00_nano, stress_00_macro_mean, "b-", label="Mean")
    # plt.plot(stress_00_nano, stress_00_macro_mean - stress_00_macro_std, "b--", label="+1 std deviation")
    # plt.plot(stress_00_nano, stress_00_macro_mean + stress_00_macro_std, "b--")
    # plt.fill_between(stress_00_nano, stress_00_macro_mean - stress_00_macro_std, stress_00_macro_mean + stress_00_macro_std,
    #                  color="b", alpha=0.2)
    # plt.plot(stress_00_nano, stress_00_macro_10_pct, "b:", label="10 and 90 percentiles")
    # plt.plot(stress_00_nano, stress_00_macro_90_pct, "b:")
    # plt.fill_between(stress_00_nano, stress_00_macro_10_pct, stress_00_macro_90_pct, color="b", alpha=0.1)
    # plt.fill_between(stress_00_nano, stress_00_macro_min, stress_00_macro_max, color="b", alpha=0.05)
    #
    # plt.legend(loc=0)
    # plt.xlabel("stress_00_nano")
    # plt.ylabel("stress_00_macro")
    # plt.savefig(os.path.join(campaign_work_dir, "stress_00_macro.png"))
    #
    # # plot the first Sobol results
    # plt.figure()
    # for k in results.sobols_first()["stress_00_macro"].keys():
    #     plt.plot(stress_00_nano, results.sobols_first()["stress_00_macro"][k], label=k)
    # plt.legend(loc=0)
    # plt.xlabel("stress_00_nano")
    # plt.ylabel("sobols_first")
    # plt.savefig(os.path.join(campaign_work_dir, "sobols_first.png"))
    #
    # # plot the second Sobol results
    # plt.figure()
    # for k1 in results.sobols_second()["stress_00_macro"].keys():
    #     for k2 in results.sobols_second()["stress_00_macro"][k1].keys():
    #         plt.plot(stress_00_nano, results.sobols_second()["stress_00_macro"][k1][k2],
    #                  label=k1 + "/" + k2)
    # plt.legend(loc=0, ncol=2)
    # plt.xlabel("stress_00_nano")
    # plt.ylabel("sobols_second")
    # plt.savefig(os.path.join(campaign_work_dir, "sobols_second.png"))
    #
    # # plot the total Sobol results
    # plt.figure()
    # for k in results.sobols_total()["stress_00_macro"].keys():
    #     plt.plot(stress_00_nano, results.sobols_total()["stress_00_macro"][k], label=k)
    # plt.legend(loc=0)
    # plt.xlabel("stress_00_nano")
    # plt.ylabel("sobols_total")
    # plt.savefig(os.path.join(campaign_work_dir, "sobols_total.png"))
    #
    # t_dist = results.raw_data["output_distributions"]["stress_00_macro"]
    # for i in [0]:
    #     plt.figure()
    #     plt.hist(results_df.stress_00_nano[i], density=True, bins=50,
    #              label="histogram of raw samples", alpha=0.25)
    #     if hasattr(t_dist, "samples"):
    #         plt.hist(t_dist.samples[i], density=True, bins=50,
    #                  label="histogram of kde samples", alpha=0.25)
    #     t1 = t_dist[i]
    #     plt.plot(
    #         np.linspace(t1.lower, t1.upper),
    #         t1.pdf(np.linspace(t1.lower, t1.upper)),
    #         label="PDF"
    #     )
    #     plt.legend(loc=0)
    #     plt.xlabel("stress_00_macro")
    #     plt.title("Distributions for stress_00_macro = %0.4f" % (stress_00_macro[i]))
    #     png_file_name = os.path.join(
    #         campaign_work_dir,
    #         "distribution_function_stress_00_macro=%0.4f.png" % (stress_00_macro[i])
    #     )
    #     plt.savefig(png_file_name)

def load_campaign_params(sampler_inputs_dir=None, machine=None):
    if str(machine) == 'localhost':
        print('\x1b[6;30;45m' + '..............................................' + '\x1b[0m')
        print('\x1b[6;30;45m' + 'loading campaign parameters for local machine!' + '\x1b[0m')
        print('\x1b[6;30;45m' + '..............................................' + '\x1b[0m')
        user_campaign_params_yaml_file = os.path.join('campaign_params_local.yml')
        campaign_params = yaml.load(open(user_campaign_params_yaml_file),
                                    Loader=yaml.SafeLoader
                                    )
        campaign_params['campaign_name'] += '-' + campaign_params['sampler_name']

    else:
        print('\x1b[6;30;45m' + '...............................................' + '\x1b[0m')
        print('\x1b[6;30;45m' + 'loading campaign parameters for remote machine!' + '\x1b[0m')
        print('\x1b[6;30;45m' + '...............................................' + '\x1b[0m')
        user_campaign_params_yaml_file = os.path.join('campaign_params_remote.yml')
        campaign_params = yaml.load(open(user_campaign_params_yaml_file),
                                    Loader=yaml.SafeLoader
                                    )
        campaign_params['campaign_name'] += '-' + campaign_params['sampler_name']


    # save campaign parameters in to a log file
    with open('campaign_params.log', 'w') as param_log:
        param_log.write('-' * 45 + '\n')
        param_log.write(" The used parameters for easyvvuq campaign\n")
        param_log.write('-' * 45 + '\n')
        yaml.dump(campaign_params, param_log, default_flow_style=False,
                  indent=4)
        param_log.write('-' * 45 + '\n\n')

    # print to campaign_params.log
    print("\ncampaign_params.log :")
    with open('campaign_params.log', 'r') as param_log:
        lines = param_log.readlines()
        print('\n'.join([line.rstrip() for line in lines]))
        return campaign_params


if __name__ == "__main__":
    # CRED = '\33[31m'
    # CEND = '\33[0m'
    # $machine_name    '$run_command'   $SCEMa_exec

    inpt = []
    inpt.append(sys.argv[1])
    inpt.append(sys.argv[2])
    inpt.append(sys.argv[3])
    work_dir1 = os.path.join(os.path.dirname(__file__))

    sampler_inputs_dir = os.path.join(work_dir1)
    init_run_analyse_campaign(work_dir=work_dir1, sampler_inputs_dir=sampler_inputs_dir, inpt=inpt)
