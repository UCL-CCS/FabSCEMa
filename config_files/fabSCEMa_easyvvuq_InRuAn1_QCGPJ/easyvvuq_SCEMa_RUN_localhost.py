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

import shutil
import tempfile
from ruamel.yaml import YAML
from pathlib import Path

# with open(lmp_input, "r") as f:

if __name__ == '__main__':
    try:
        commandstring = ''

        for arg in sys.argv[3:]:  # skip sys.argv[0] since the question didn't ask for it
            if ' ' in arg:
                commandstring += '"{}"  '.format(arg)  # Put the quotes back in

            else:
                commandstring += "{}  ".format(arg)


        SCEMa_exec = commandstring.split(sep=',').pop(2)
        SCEMa_exec = SCEMa_exec.replace("'", "").strip().replace("]", "")

        run_command = commandstring.split(sep=',').pop(1)
        run_command = run_command.replace("'", "").strip()
        run_command = run_command.split()

        string = SCEMa_exec
        run_command.append(string)

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
        # works up here
        in_macro_csv_path = './macroscale_log/loadedbc_force.csv'
        columns_to_be_removed1 = ['timestep', 'time']

        data_macro = pd.read_csv(in_macro_csv_path).drop(columns_to_be_removed1, axis='columns')
        data_macro.to_csv('output_macro_original.csv',
                          index=None, header=False)

        data_macro2 = pd.read_csv('output_macro_original.csv')
        data_macro2 = np.array(data_macro2)
        print('macro dada shape:', data_macro2.shape)
        print('output macro to csv')
        col_Names = ["resulting_force"]
        my_CSV_File = pd.read_csv("output_macro_original.csv", names=col_Names).fillna(0.0)
        my_CSV_File.to_csv("output.csv", index=None)
    except:
        print("system error, terminating!")
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)
