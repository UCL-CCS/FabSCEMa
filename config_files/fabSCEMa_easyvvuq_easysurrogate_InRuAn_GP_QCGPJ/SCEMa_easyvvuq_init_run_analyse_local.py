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
import easysurrogate as es
import easyvvuq as uq
import time
import pickle
import matplotlib
if not os.getenv("DISPLAY"):
    matplotlib.use("Agg")
import matplotlib.pylab as plt
from easyvvuq.actions import QCGPJPool
from operator import add
from easysurrogate.analysis.base import BaseAnalysis
import time as t
import sys

def print_to_file(str=None, results=None, campaign_work_dir=None):

    results.plot_moments(qoi="{}".format(str), ylabel="{}".format(str), xlabel="Time", alpha=0.2,
                         filename=os.path.join(campaign_work_dir, '{}_moments.png'.format(str)))
    results.plot_sobols_first(
        qoi="{}".format(str), xlabel="Time",
        filename=os.path.join(campaign_work_dir, '{}_sobol_first.png'.format(str))
    )

    rho11 = results.describe('{}'.format(str), 'mean')
    for k in results.sobols_total()['{}'.format(str)].keys():
        plt.plot(rho11, results.sobols_total()['{}'.format(str)][k], label=k)
    plt.legend(loc=0)
    plt.xlabel('{} [Pa]'.format(str))
    plt.ylabel('sobol_total')
    plt.title('{}'.format(str))
    plt.savefig(os.path.join(campaign_work_dir, '{}_sobols_total.png'.format(str)))
    print("saving {}_sobol_total.png -->".format(str),
          os.path.join(campaign_work_dir, '{}_sobol_total.png'.format(str)))

    rho12 = results.describe('{}'.format(str), 'mean')
    for k1 in results.sobols_second()['{}'.format(str)].keys():
        for k2 in results.sobols_second()['{}'.format(str)][k1].keys():
            plt.plot(rho12, results.sobols_second()['{}'.format(str)][k1][k2], label=k1 + '/' + k2)
    plt.legend(loc=0, ncol=2)
    plt.xlabel('{} [Pa]'.format(str))
    plt.ylabel('sobol_second')
    plt.title('{}'.format(str))
    plt.savefig(os.path.join(campaign_work_dir, '{}_sobol_second.png'.format(str)))
    print("saving {}_sobol_second.png -->".format(str),
          os.path.join(campaign_work_dir, '{}_sobol_second.png'.format(str)))


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

    if str(machine_name) == 'localhost':
        print('\x1b[6;30;45m' + '.........................' + '\x1b[0m')
        print('\x1b[6;30;45m' + 'running on local machine!' + '\x1b[0m')
        print('\x1b[6;30;45m' + '.........................' + '\x1b[0m')
        print('os.getcwd()', os.getcwd())
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
    # campaign.execute(pool=client).collate()
    with QCGPJPool(template_params={'venv': '/home/kevin/venv'}) as qcgpj:
        campaign.execute(pool=qcgpj).collate(progress_bar=True)
    # campaign.set_sampler(sampler)
    #
    # campaign.execute(nsamples=5).collate()

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
            qoi_cols=["stress_00_macro", "stress_01_macro", "stress_02_macro", "stress_11_macro", "stress_12_macro",
                      "stress_22_macro", "stress_00_nano", "stress_01_nano", "stress_02_nano", "stress_11_nano",
                      "stress_12_nano", "stress_22_nano"]
            # qoi_cols=['stress_00_macro', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro', 'stress_12_macro',
            #           'stress_22_macro', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano',
            #           'stress_12_nano', 'stress_22_nano']
        )
    elif campaign_params['sampler_name'] == 'PCESampler':
        analysis = uq.analysis.PCEAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["stress_00_macro", "stress_01_macro", "stress_02_macro", "stress_11_macro", "stress_12_macro",
                      "stress_22_macro", "stress_00_nano", "stress_01_nano", "stress_02_nano", "stress_11_nano",
                      "stress_12_nano", "stress_22_nano"]
            # qoi_cols=['stress_00_macro', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro', 'stress_12_macro',
            #           'stress_22_macro', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano',
            #           'stress_12_nano', 'stress_22_nano']
        )
    elif campaign_params['sampler_name'] == 'QMCSampler':
        analysis = uq.analysis.QMCAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["stress_00_macro", "stress_01_macro", "stress_02_macro", "stress_11_macro", "stress_12_macro",
                      "stress_22_macro", "stress_00_nano", "stress_01_nano", "stress_02_nano", "stress_11_nano",
                      "stress_12_nano", "stress_22_nano"]
            # qoi_cols=['stress_00_macro', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro', 'stress_12_macro',
            #           'stress_22_macro', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano',
            #           'stress_12_nano', 'stress_22_nano']
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
    # results_df = campaign.get_collation_result()
    results = campaign.get_last_analysis()


    print("descriptive statistics :")
    # print(results.describe("stress_00_macro"))
    # print("the first order sobol index :")
    # print(results.sobols_first()['stress_00_macro'])

    # mean = results.describe("stress_00_macro", "mean")
    # var = results.describe("stress_00_macro", "var")
    #

    for s_string in output_column:
        print_to_file(str=s_string, results=results, campaign_work_dir=campaign_work_dir)

    time_end = time.time()
    print("Time for phase 7 = %.3f" % (time_end - time_start))
    time_start = time.time()

    pickle_file = os.path.join(campaign_work_dir, "SCEMa.pickle")
    with open(pickle_file, "bw") as f_pickle:
        pickle.dump(results, f_pickle)

    time_end = time.time()
    print("Time for phase 8 = %.3f" % (time_end - time_start))

    print('\x1b[6;30;42m' + '...................................' + '\x1b[0m')
    print('\x1b[6;30;42m' + 'Starting an EasySurrogate campaign!' + '\x1b[0m')
    print('\x1b[6;30;42m' + '...................................' + '\x1b[0m')

    sur_campaign = es.Campaign(name=campaign_params['sub_campaign_name'])

    # load the training data
    x = np.arange(len(vary))
    mean_all = np.zeros_like(x)
    # output_column = ["stress_00_macro"]
    for string_l in output_column:
        print('\x1b[6;30;42m' + "string roi:" + '\x1b[0m', string_l)
        arg1, arg2 = ess_result_output(campaign, campaign_work_dir, output_column, sampler, sur_campaign, srtn=string_l)
        # idx_t.append(arg2)
        # mean_grad_t.append(arg1)
        mean_all = mean_all + arg1

    # plt.show()
    mean_all = mean_all / len(output_column)

    print("mean", mean_all)
    mean_all = (mean_all - np.min(mean_all)) / (np.max(mean_all) - np.min(mean_all))
    print("mean", mean_all)
    n = len(mean_all)
    ranked = np.argsort(np.array(mean_all))
    idxx = ranked[::-1][:n]
    print('Parameters ordered from most to least important:')

    # idxx = np.argsort(mean_all)
    params_ordered = np.array(list(sampler.vary.get_keys()))[idxx]
    fig = plt.figure('sensitivity', figsize=[4, 8])
    ax = fig.add_subplot(111)
    # ax.set_ylabel(r'$\int\frac{\partial ||y||^2_2}{\partial x_i}p(x)dx$', fontsize=14)
    ax.set_ylabel(r'$\nabla E[f_{*}|X,y,x_{*}]$', fontsize=14)
    mean_all = [mean_all[index] for index in idxx]
    # find max quad order for every parameter
    ax.bar(range(len(mean_all)), height=mean_all)
    ax.set_xticks(range(len(mean_all)))
    ax.set_xticklabels(params_ordered)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(campaign_work_dir, '{}_sensitivity.png'.format("total_mean")))
    plt.close()

    print('\x1b[6;30;41m' + '.........................' + '\x1b[0m')
    print('\x1b[6;30;41m' + 'Problem analysis is done!' + '\x1b[0m')
    print('\x1b[6;30;41m' + '.........................' + '\x1b[0m')


def sensitivity_measures(surrogate, feats, dm):
    N = feats.shape[0]
    print("feats.shape", N)
    x = np.arange(dm)
    mean = np.zeros_like(x)
    for i in range(N):
        tmp = np.reshape(feats[i], (dm, 1))
        # x = tmp / np.linalg.norm(tmp)

        Alpha = surrogate.model.instance.alpha_
        constant_value = 1.0
        constant_value_bounds = (1e-6, 1e+6)
        length_scale = 1.0
        length_scale_bounds = (length_scale * 1e-4, length_scale * 1e+4)

        df_dx = []
        for j in range(len(tmp[:, 0])):
            f1 = np.array(surrogate.X_train).shape[0]
            f2 = np.array(surrogate.X_train).shape[1]
            xd = tmp[:, 0][j].reshape(1, -1) - surrogate.X_train.reshape(1, -1)
            f = np.exp(-xd ** 2 / (2 * length_scale ** 2))
            df = (f * (-xd / length_scale ** 2))
            dtm = constant_value * df
            dtm = np.array(dtm).reshape(f2, f1)
            dtm = dtm @ Alpha
            dtm = np.sum(dtm, axis=1)
            df_dx.append(dtm[j] / N)

        mean = list(map(add, mean, df_dx))

    # print("mean", mean)
    mean = (mean - np.min(mean)) / (np.max(mean) - np.min(mean))
    mean = np.nan_to_num(mean)
    print("mean", mean)
    n = len(mean)
    ranked = np.argsort(np.array(mean))
    idx = ranked[::-1][:n]
    print('Parameters ordered from most to least important:')
    print(idx)
    return idx, mean


def ess_result_output(campaign, campaign_work_dir, output_column, sampler, sur_campaign, srtn=None):
    output_columns_i = ["{}".format(srtn)]
    params_su, samples_su = sur_campaign.load_easyvvuq_data(campaign, qoi_cols=output_columns_i)
    samples_su = samples_su["{}".format(srtn)]
    samples_su = samples_su / np.linalg.norm(samples_su)
    params_su = params_su / np.linalg.norm(params_su)
    D1 = params_su.shape[1]
    D0 = params_su.shape[0]
    S1 = samples_su.shape[1]
    print("params.shape[0]----->", params_su.shape[0])
    print("params.shape[1]----->", params_su.shape[1])
    # dimension_active_subspace = 2
    time_init_start = t.time()
    surrogate = es.methods.GP_Surrogate(n_in=D1, n_out=S1, basekernel='RBF')
    print('Time to initialise the surrogate: {:.3} s'.format(t.time() - time_init_start))
    time_train_start = t.time()
    surrogate.train(feats=params_su, target=samples_su, test_frac=0.2)
    feat_train, targ_train, feat_test, targ_test = surrogate.feat_eng.get_training_data(params_su, samples_su,
                                                                                        index=surrogate.feat_eng.train_indices)
    print("feat_train", feat_train.shape)
    print("targ_train", targ_train.shape)
    print("feat_test", feat_test.shape)
    print("targ_test", targ_test.shape)
    print('Time to train the surrogate: {:.3} s'.format(t.time() - time_train_start))
    dims = {}
    dims['n_train'] = surrogate.model.n_train
    dims['n_samples'] = samples_su.shape[0]
    dims['n_test'] = dims['n_samples'] - dims['n_train']
    print("dims", dims)
    n_mc = dims['n_train']
    pred = np.zeros([n_mc, S1])
    st = np.zeros([n_mc, S1])

    for i in range(n_mc):
        pred[i, :], st[i, :] = surrogate.predict(np.reshape(params_su[i], (D1, 1)))

    train_data = samples_su[0:dims['n_train']]
    print("train_data - pred", np.linalg.norm(train_data - pred))
    # print("pred",  pred)
    print("np.linalg.norm(train_data)", np.linalg.norm(train_data))
    rel_err_train = np.linalg.norm(train_data - pred) / np.linalg.norm(train_data)
    # run the trained model forward at test locations
    pred = np.zeros([dims['n_test'], S1])
    st = np.zeros([dims['n_test'], S1])
    for idx, i in enumerate(range(dims['n_train'], dims['n_samples'])):
        pred[idx], st[idx] = surrogate.predict(np.reshape(params_su[i], (D1, 1)))

    test_data = samples_su[dims['n_train']:]
    rel_err_test = np.linalg.norm(test_data - pred) / np.linalg.norm(test_data)
    # print('================================')
    # print('Relative error on training set = %.4f' % rel_err_train)
    # print('Relative error on test set = %.4f' % rel_err_test)
    # print('================================')

    # create DAS analysis object
    analysis = es.analysis.GP_analysis(surrogate)
    # analysis.plot_2d_design_history(x_test=feat_test, y_test=targ_test)
    analysis.get_regression_error(feat_test, targ_test, feat_train, targ_train)
    # draw MC samples from the inputs
    new_samples = campaign.get_active_sampler().count * 100
    # new_samples = 1
    print("New samples from the inputs:", new_samples)
    params_nw = np.array([p.sample(new_samples) for p in sampler.vary.get_values()]).T

    # idx, mean_grad = sensitivity_measures(surrogate, params_nw, D1)
    idx, mean_grad = sensitivity_measures(surrogate, params_nw, D1)
    # params_ordered = np.array(list(sampler.vary.get_keys()))[idx[0]]
    params_ordered = np.array(list(sampler.vary.get_keys()))[idx]
    fig = plt.figure('sensitivity', figsize=[4, 8])
    ax = fig.add_subplot(111)
    # ax.set_ylabel(r'$\int\frac{\partial ||y||^2_2}{\partial x_i}p(x)dx$', fontsize=14)
    ax.set_ylabel(r'$\nabla E[f_{*}|X,y,x_{*}]$', fontsize=14)

    # find max quad order for every parametera.ravel()
    # ax.bar(range(len(mean_grad)), height=mean_grad[idx].flatten())
    mean_grad = [mean_grad[index] for index in idx]
    print("mean_grad", mean_grad)
    print("mparams_ordered", params_ordered)
    ax.bar(range(len(mean_grad)), height=mean_grad)
    ax.set_xticks(range(len(mean_grad)))
    ax.set_xticklabels(params_ordered)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(campaign_work_dir, '{}_sensitivity.png'.format(output_columns_i)))
    plt.close()
    return mean_grad, idx


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
