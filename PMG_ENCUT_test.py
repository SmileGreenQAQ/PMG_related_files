# -*- coding: utf-8 -*-
"""
Created on Mon May 22 20:28:58 2023

@author: Ayris CHENG

ENCUT test
"""
#%%
def main():
    from pymatgen.core.structure import Structure
    from pymatgen.io.vasp.inputs import Incar
    import pandas as pd
    
    incar = Incar.from_file('INCAR')
    structure = Structure.from_file('POSCAR')
    set_potcar = 'echo -e "103\n" | vaspkit'
    vasp_exe = '$VASP_EXECUTION >& log'
    record_file = 'record_file'
    with open ('record_file', 'a') as fh: fh.write('='*60+'\n')
    
    # ENCUT step critiria
    converged_criterion = 0.1 # in eV


#%%
def ENCUT_cal():
    # import modules
    import os
    import shutil
    from pymatgen.io.vasp.outputs import Outcar
    
    