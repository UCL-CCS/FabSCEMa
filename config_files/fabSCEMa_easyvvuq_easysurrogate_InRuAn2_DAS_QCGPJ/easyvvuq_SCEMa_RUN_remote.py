#!/usr/bin/env python3

import sys
import numpy as np
import json


import json
import numpy as np
import os
import sys
import signal
import subprocess
import time
import shlex
import platform
import xml.etree.ElementTree as ET
import pandas as pd

work_dirx = os.path.dirname(os.path.abspath(__file__))
# c_work_dir = os.path.join(work_dirx, 'in.lammps')
from pathlib import Path
curr_dir=Path(os.path.dirname(os.path.abspath(__file__)))
two_dir_up_=os.fspath(Path(curr_dir.parent.parent).resolve())
SCEMa_input = sys.argv[1]
c_path = sys.argv[2]

# with open(SCEMa_input, 'r') as fd:
#     inputs = json.load(fd)
#
# print("number of sampling steps: " + str(inputs['molecular dynamics parameters']["number of sampling steps"]))
import shutil
import tempfile
from ruamel.yaml import YAML
from pathlib import Path

# with open(lmp_input, "r") as f:
number_of_sampling_steps_nano = 100
len_qpid_macro = 16
if __name__ == '__main__':
    try:
        commandstring = ''

        for arg in sys.argv[3:]:  # skip sys.argv[0] since the question didn't ask for it
            if ' ' in arg:
                commandstring += '"{}"  '.format(arg)  # Put the quotes back in

            else:
                commandstring += "{}  ".format(arg)
        # ['localhost', 'mpirun -np 1', '/home/kevin/Desktop/FSCEMA/SCEMa/dealammps']
        # ['localhost', 'mpirun -np 1', '/home/kevin/Desktop/working/lammps-29Sep2021/src/lmp_serial',
        #  '-log log.lammps -screen [lammps_scr_output.txt']

        SCEMa_exec = commandstring.split(sep=',').pop(2)
        SCEMa_exec = SCEMa_exec.replace("'", "").strip().replace("]", "")

        run_command = commandstring.split(sep=',').pop(1)
        run_command = run_command.replace("'", "").strip()
        run_command = run_command.split()

        # lammps_args = commandstring.split(sep=',').pop(3)
        # lammps_args = lammps_args.replace("'", "").strip()
        # lammps_args = lammps_args.split()
        string = SCEMa_exec
        run_command.append(string)
        # for i in range(0, len(lammps_args)):
        #     run_command.append(lammps_args[i])

        print("checking run_command", run_command)
    except:
        print("system error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    return_code = -1
    try:
        print("Executing easyvvuq with FabSCEMa ...")
        # work_dirx = os.path.dirname(os.path.abspath(__file__))
        first = os.listdir('..')[0]
        sec = os.listdir('../..')[0]
        lm1 = c_path + '/' + str(sec) + '/' + str(first) + '/'
        px = os.listdir(two_dir_up_)
        pv = c_path + '/' + str(sec) + '/' + str(first) + '/output.csv'
        pep1x = work_dirx + '/parse_SCEMa_macro_nano_log.py'
        pep2x = c_path + '/' + str(sec) + '/' + str(first) + '/parse_SCEMa_macro_nano_log.py'
        # shutil.copy(os.path.join(pep1x), os.path.join(pep2x))

        c_work_dir = os.path.join(lm1, SCEMa_input)

        run_command.append(SCEMa_input)
        print("run_command", run_command)
        process = subprocess.Popen(run_command,
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True)

        while True:
            output = process.stdout.readline()
            print(output.strip())
            # Do something else
            return_code = process.poll()
            if return_code is not None:
                print('RETURN CODE', return_code)
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    print(output.strip())
                break
    except:
        print("system error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)
    # json_input = 'inputs.json'
    # cell_id_list = './macroscale_output/cell_id_mat.list'
    # with open(json_input, 'r') as fd:
    #     inputs = json.load(fd)
    # # list_file = open(cell_id_list)
    # count = 0
    # with open(cell_id_list, 'r') as fdx:
    #     for line in fdx:
    #         count = count + 1
    # print('cell id mat count:', count)
    # print("number of sampling steps: " + str(inputs['molecular dynamics parameters']["number of sampling steps"]))

    # len_qpid_macro = int(count)
    # number_of_sampling_steps_nano = int(inputs['molecular dynamics parameters']["number of sampling steps"])

    try:
        in_macro_csv_path = './macroscale_log/pr_0.lhistory.csv'
        columns_to_be_removed1 = ['timestep', 'time', 'qpid', 'cell', 'qpoint', 'material', 'strain_00',
                                  'strain_01', 'strain_02', 'strain_11', 'strain_12', 'strain_22', 'updstrain_00',
                                  'updstrain_01', 'updstrain_02', 'updstrain_11', 'updstrain_12', 'updstrain_22']
        columnsn = ['index', 'stress_00_macro', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro',
                    'stress_12_macro', 'stress_22_macro']

        data_macro = pd.read_csv(in_macro_csv_path).drop(columns_to_be_removed1, axis='columns')
        data_macro.to_csv('output_macro1.csv',
                          index=None, header=False)

        data_macro2 = pd.read_csv('output_macro1.csv')
        data_macro2 = np.array(data_macro2)
        print('macro dada shape:', data_macro2.shape)
        X_macro = []
        for i in range(data_macro2.shape[1]):
            tmp = []
            for j in range(int((data_macro2.shape[0]) / len_qpid_macro)):
                tmp.append((np.sum(data_macro2[(j + 1) * len_qpid_macro:(j + 1) * len_qpid_macro + len_qpid_macro, i])) / len_qpid_macro)

            X_macro.append(tmp)
        Y_macro = np.array(X_macro).transpose()
        ltx = []
        for k in range(len(Y_macro)):
            ltx.append(np.append(k, Y_macro[k]))
        print('output macro to csv')
        np.savetxt("output_macro.csv", ltx, delimiter=",",
                   header="index,stress_00_macro,stress_01_macro,stress_02_macro,stress_11_macro,stress_12_macro,stress_22_macro",
                   comments='')
    except:
        print("system/file error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    try:
        columns_to_be_removed2 = ['qp_id', 'material_id', 'time_id', 'temperature', 'strain_rate', 'force_field',
                                  'replica_id', 'strain_00', 'strain_01', 'strain_02', 'strain_11', 'strain_12',
                                  'strain_22']
        columnsm = ['index', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano',
                    'stress_12_nano',
                    'stress_22_nano']

        for i in range(len_qpid_macro):
            in_nano_csv_path = './nanoscale_output/mddata_qpid{}_repl1.csv'.format(i)
            data_nano = pd.read_csv(in_nano_csv_path).drop(columns_to_be_removed2, axis='columns')
            data_nano.to_csv('output_nano{}.csv'.format(i),
                             index=None, header=False)
    except:
        print("system/file error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    try:
        Y1 = 0
        for i in range(len_qpid_macro):
            data_nano1 = pd.read_csv('output_nano{}.csv'.format(i))
            data_nano1 = np.array(data_nano1)
            X1_nano = []
            if i > 7:
                for k in range(data_nano1.shape[1]):
                    tmp = []
                    for j in range(int((data_nano1.shape[0]) / number_of_sampling_steps_nano)):
                        tmp.append((np.sum(data_nano1[(j + 1) * number_of_sampling_steps_nano:(j + 1) * number_of_sampling_steps_nano + number_of_sampling_steps_nano, k])) / number_of_sampling_steps_nano)
                    X1_nano.append(tmp)
            else:
                for k in range(data_nano1.shape[1]):
                    tmp = []
                    for j in range(int((data_nano1.shape[0] + 1) / number_of_sampling_steps_nano)):
                        tmp.append((np.sum(data_nano1[j * number_of_sampling_steps_nano:j * number_of_sampling_steps_nano + number_of_sampling_steps_nano, k])) / number_of_sampling_steps_nano)
                    X1_nano.append(tmp)

            Y1 = np.array(X1_nano).transpose() + Y1
    except:
        print("system/file error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    try:
        Y1 = Y1 / len_qpid_macro
        lty = []

        for k in range(len(Y1)):
            lty.append(np.append(k, Y1[k]))
        print('output nano to csv')
        np.savetxt("output_nano.csv", lty, delimiter=",",
                   header="index,stress_00_nano,stress_01_nano,stress_02_nano,stress_11_nano,stress_12_nano,stress_22_nano",
                   comments='')

    except:
        print("system/file error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    try:
        print('combining macro and nano ...')
        data1 = pd.read_csv('output_macro.csv').fillna(0.0)
        data2 = pd.read_csv('output_nano.csv').fillna(0.0)
        columnsf = ['index', 'stress_00_macro', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro',
                    'stress_12_macro', 'stress_22_macro', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano',
                    'stress_11_nano', 'stress_12_nano', 'stress_22_nano']
        # columnsr = ['index', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro', 'stress_12_macro',
        #             'stress_22_macro', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano',
        #             'stress_12_nano',
        #             'stress_22_nano']
        columnsr = ['index']
        output3 = pd.merge(data1, data2, on='index', how='right')
        output3.to_csv('output.csv', index=False, header=False)
        # result_path = c_path + '/' + str(sec) + '/' + str(first) + '/result.csv'
        print('writing final results ...')
        my_File = pd.read_csv('output.csv', quotechar="'", names=columnsf)
        my_File.to_csv('output.csv',
                       index=None)
        data_macrox = pd.read_csv('output.csv').drop(columnsr, axis='columns')
        data_macrox.to_csv('output.csv',
                           index=None, header=False)
        cols = ['stress_00_macro', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro', 'stress_12_macro',
                'stress_22_macro', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano',
                'stress_12_nano', 'stress_22_nano']
        CSV_Fileyy = pd.read_csv('output.csv', quotechar="'", names=cols).fillna(0.0)
        CSV_Fileyy.to_csv('output.csv',
                          index=None)

    except:
        print("system/file error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)


