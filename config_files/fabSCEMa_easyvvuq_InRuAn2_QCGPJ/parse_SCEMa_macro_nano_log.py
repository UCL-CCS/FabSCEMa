import re
import csv
import os
import sys
import signal
import subprocess
import time
import pandas as pd
import numpy as  np
# lmp_input = sys.argv[1]
# csv_input = sys.argv[2]
len_qpid_macro = 16
number_of_sampling_steps_nano = 100
try:
    in_macro_csv_path ='./macroscale_log/pr_0.lhistory.csv'
    columns_to_be_removed1 = ['timestep','time','qpid','cell','qpoint','material','strain_00','strain_01','strain_02','strain_11','strain_12','strain_22','updstrain_00','updstrain_01','updstrain_02','updstrain_11','updstrain_12','updstrain_22']
    columnsn = ['index','stress_00_macro','stress_01_macro','stress_02_macro','stress_11_macro','stress_12_macro','stress_22_macro']

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
            tmp.append((np.sum(data_macro2[(j+1)*len_qpid_macro:(j+1)*len_qpid_macro + len_qpid_macro, i])) / len_qpid_macro)

        X_macro.append(tmp)
    Y_macro = np.array(X_macro).transpose()
    ltx = []
    for k in range(len(Y_macro)):
        ltx.append(np.append(k, Y_macro[k]))
    print('output macro to csv')
    np.savetxt("output_macro.csv", ltx, delimiter=",", header="index,stress_00_macro,stress_01_macro,stress_02_macro,stress_11_macro,stress_12_macro,stress_22_macro",
               comments='')
except:
    print("system/file error, terminating!")
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)

try:
    columns_to_be_removed2 = ['qp_id', 'material_id', 'time_id', 'temperature', 'strain_rate', 'force_field',
                              'replica_id', 'strain_00', 'strain_01', 'strain_02', 'strain_11', 'strain_12',
                              'strain_22']
    columnsm = ['index', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano', 'stress_12_nano',
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
                    tmp.append((np.sum(data_nano1[(j+1)*number_of_sampling_steps_nano:(j+1)*number_of_sampling_steps_nano + number_of_sampling_steps_nano, k])) / number_of_sampling_steps_nano)
                X1_nano.append(tmp)
        else:
            for k in range(data_nano1.shape[1]):
                tmp = []
                for j in range(int((data_nano1.shape[0] + 1) / number_of_sampling_steps_nano)):
                    tmp.append((np.sum(data_nano1[j*number_of_sampling_steps_nano:j*number_of_sampling_steps_nano + number_of_sampling_steps_nano, k])) / number_of_sampling_steps_nano)
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
    np.savetxt("output_nano.csv", lty, delimiter=",", header="index,stress_00_nano,stress_01_nano,stress_02_nano,stress_11_nano,stress_12_nano,stress_22_nano",
                comments='')

except:
    print("system/file error, terminating!")
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)


try:
    print('combining macro and nano ...')
    data1 = pd.read_csv('output_macro.csv')
    data2 = pd.read_csv('output_nano.csv')
    columnsf = ['index','stress_00_macro','stress_01_macro','stress_02_macro','stress_11_macro','stress_12_macro','stress_22_macro', 'stress_00_nano', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano', 'stress_12_nano',
                'stress_22_nano']
    columnsr = ['index', 'stress_01_macro', 'stress_02_macro', 'stress_11_macro', 'stress_12_macro',
                'stress_22_macro', 'stress_01_nano', 'stress_02_nano', 'stress_11_nano',
                'stress_12_nano',
                'stress_22_nano']
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
    cols = ['stress_00_macro', 'stress_00_nano']
    CSV_Fileyy = pd.read_csv('output.csv', quotechar="'", names=cols)
    CSV_Fileyy.to_csv('output.csv',
                 index=None)

except:
    print("system/file error, terminating!")
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)

