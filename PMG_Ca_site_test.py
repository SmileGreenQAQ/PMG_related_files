#!/home/u3130253/.conda/envs/pymatgen_envs/bin/python3.1
"""
Created on Sat Jul  1 14:12:50 2023
This code can read the file of Na site in MCMO (Na_site.dat)
1. Put Ca into Na site
2. Relaxation
3. Calculate Ca removal energy

@author: Ayris
"""
#%%
def main():
    #from pymatgen.core.structure import Structure
    #from pymatgen.io.vasp.inputs import Incar
    #incar = Incar.from_file('INCAR')
    #structure = Structure.from_file('POSCAR')
    #set_potcar = 'echo -e "103\n" | vaspkit'
    Na_sites = [[1.00000000, 1.00000000, 0.25000000],
 [0.66666700, 1.00000000, 0.25000000],
 [1.00000000, 0.33333300, 0.25000000],
 [0.33333300, 0.33333300, 0.25000000],
 [0.66666700, 0.33333300, 0.25000000],
 [1.00000000, 0.66666700, 0.25000000],
 [0.33333300, 0.66666700, 0.25000000],
 [0.33333300, 1.00000000, 0.25000000],
 [0.66666700, 0.66666700, 0.25000000],
 [0.11111100, 0.22222200, 0.25000000],
 [0.77777800, 0.22222200, 0.25000000],
 [0.11111100, 0.55555500, 0.25000000],
 [0.44444400, 0.55555500, 0.25000000],
 [0.77777800, 0.55555500, 0.25000000],
 [0.11111100, 0.88888900, 0.25000000],
 [0.44444400, 0.88888900, 0.25000000],
 [0.44444400, 0.22222200, 0.25000000],
 [0.77777800, 0.88888900, 0.25000000]]
    vasp_exe = '$VASP_EXECUTION >& log'
    relaxation = 'lattice_optimization.py'
    record_file = 'record_file'
    final_E = []
    final_E = dope_Ca(Na_sites, relaxation, vasp_exe, record_file, final_E)
    cal_removal_energy(final_E)
    
#%%
def dope_Ca(Na_sites, relaxation, vasp_exe, record_file, final_E):
    import copy
    import os
    import shutil
    from pymatgen.io.vasp.inputs import Poscar
    from pymatgen.core.structure import Structure
    from pymatgen.io.vasp.outputs import Oszicar
    for i in range(len(Na_sites)):
        if not os.path.isdir('site_%d' % (i+1)):
            structure = Structure.from_file('POSCAR')
            os.mkdir('site_%d' % (i+1)) # Create an dir for each site
            doped_structure = copy.deepcopy(structure) 
            doped_structure.append('Ca', Na_sites[i]) # Dope Ca into the site
            Poscar(doped_structure).write_file('doped_structure') # Write file
            shutil.copyfile('doped_structure','site_%d/POSCAR' % (i+1)) 
            shutil.copyfile('KPOINTS', 'site_%d/KPOINTS' % (i+1))
            shutil.copyfile('INCAR', 'site_%d/INCAR' % (i+1))
            os.chdir('./site_%d' % (i+1))
            os.system(relaxation) # Do relaxation
            oszicar = Oszicar('OSZICAR')
            final_E.append(oszicar.final_energy)
            os.chdir('../')
            with open(record_file, 'a') as fh: fh.write('Done site_%d relaxation.\n' % (i+1))
        else:
            os.chdir('./site_%d' % (i+1))
            oszicar = Oszicar('OSZICAR')
            final_E.append(oszicar.final_energy)
            os.chdir('../')
    return final_E 
#%%
def cal_removal_energy(final_E):
    Ca_E = -1.9283569
    MCMO_E = -343.06779
    cal_removal_E = []
    for i in final_E:
        cal_removal_E.append((i - MCMO_E - Ca_E))
    with open('Ca_removal_E.dat', 'w') as fh: fh.writelines(cal_removal_E)
#%%
if __name__ == '__main__':
    main()           
        
        
