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
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '../')


def test_SCEMa():
    assert(subprocess.call(["fabsim", "localhost", "SCEMa:SCEMa_test1"]) == 0)
    assert (subprocess.call(["fabsim", "localhost", "SCEMa:SCEMa_test2"]) == 0)
  
def test_SCEMa_ensemble1():
    assert(subprocess.call(["fabsim", "localhost", "SCEMa_ensemble:SCEMa_ensemble_example1"]) == 0)
    assert (subprocess.call(["fabsim", "localhost", "SCEMa_ensemble:SCEMa_ensemble_example2"]) == 0)
