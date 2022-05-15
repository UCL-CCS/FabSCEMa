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
    in_macro_csv_path ='./macroscale_log/loadedbc_force.csv'
    columns_to_be_removed1 = ['timestep','time']

    data_macro = pd.read_csv(in_macro_csv_path).drop(columns_to_be_removed1, axis='columns')
    data_macro.to_csv('output_macro1.csv',
                 index=None, header=False)

    data_macro2 = pd.read_csv('output_macro1.csv')
    data_macro2 = np.array(data_macro2)
    print('macro dada shape:', data_macro2.shape)
    print('output macro to csv')
    col_Names = ["resulting_force"]
    my_CSV_File = pd.read_csv("output_macro1.csv", names=col_Names)
    my_CSV_File.to_csv("output.csv", index=None)
    # np.savetxt("output_macrovv.csv", data_macro2, delimiter=",", header="resulting_force",
    #            comments='')
except:
    print("system/file error, terminating!")
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)





