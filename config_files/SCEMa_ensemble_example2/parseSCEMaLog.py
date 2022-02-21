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
with open('log.lammps', 'r') as f:

    pattern = 'Step.*?\n(.*?)Loop'
    string = f.read()
    print('reading log.lammps')
    extracted_data = []
    for total_data in re.findall(pattern, string, flags=re.DOTALL): 
        for line in total_data.splitlines():
            extracted_data.append(line.split())

with open('output.csv', 'w', newline='') as f:
    print('writing output.csv')
    write = csv.writer(f)
    write.writerows(extracted_data)

columns = ['solvation_energy']

in_txt = pd.read_csv('output.csv')
in_txt = np.array(in_txt)
lety = []
for i in range(0, len(in_txt)):
     lety.append(np.append(i, np.fromstring(str(in_txt[i][10]).replace(' ', ','), dtype=float, sep=',')))
# print('output2 noheader to csv ...')
np.savetxt('output.csv', lety, delimiter=",")
CSV_Filex = pd.read_csv('output.csv', quotechar="'", names=columns)
# CSV_Filex.drop(labels='""')
CSV_Filex = CSV_Filex.dropna()
print('output1 with header to csv ...')

CSV_Filex.to_csv('output.csv',
                 index=None)

