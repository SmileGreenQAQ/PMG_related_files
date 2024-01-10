#!/home/u3130253/.conda/envs/pymatgen_envs/bin/python3.10
"""
Created on Tue Mar  7 11:00:11 2023

@author: Henry, Ayris

Kpoint test
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
    
    # Kpoint settings
    converged_criterion = 0.1 # in eV
    kmesh, E_list, KPT = test_kpt(converged_criterion, incar, structure, set_potcar, vasp_exe, record_file) # ??
    kpt_data = {'kmesh':kmesh, 'K points':KPT, 'Total E': E_list}
    df1 = pd.DataFrame(kpt_data)
    with open('KPT_data.dat', 'w') as fh: fh.write(str(df1))
    plot_fig(kmesh, E_list)
    
#%%
def test_kpt(converged_criterion, incar, structure, set_potcar, vasp_exe, record_file):
    """
    

    Parameters
    ----------
    converged_criterion : float
        DESCRIPTION. The converged criterion to stop testing
    incar : pymatgen.io.vasp.inputs.Incar
        DESCRIPTION. pymatgen.io.vasp.inputs.Incar object => use obj.write_file('filename') to write
    structure : pymatgen.core.structure.Structure
        DESCRIPTION. The Structure obj. => Poscar(structure).write_file('filename') write
    set_potcar : str
        DESCRIPTION. The system command for os.system() func. to generate POTCAR
    vasp_exe : str
        DESCRIPTION. The system command for os.system() func. to run VASP
    record_file : str
        DESCRIPTION. Record every thing happening

    Returns
    -------
    kmesh : list
        DESCRIPTION. Kmesh-Resolved Value (in Units of 2*PI/Angstrom)
    E_list : list
        DESCRIPTION. Total energy of different k mesh
    KPT : list
        DESCRIPTION. Kpoints in KPOINTS file

    """
    # import modules
    import os
    import shutil
    from pymatgen.io.vasp.outputs import Outcar
   
    kmesh_value = 0.06 # default value
    dir_num = [] ; E_list = [] ; kmesh = []; KPT = []

    # make sure gamma point is tested
    if '0' not in os.listdir():
        os.mkdir('0') # make directory
        shutil.copyfile('POSCAR','0/POSCAR')
        shutil.copyfile('INCAR', '0/INCAR')
        os.chdir('./0') # enter directory
        os.system('echo -e "102\n2\n0" | vaspkit') # create KPOINTS file by using vaspkit
        vasp_cal(incar, structure, set_potcar, vasp_exe, record_file) # run vasp
        outcar_obj = Outcar('OUTCAR')
        E_list.append(outcar_obj.final_energy) ; dir_num.append(0); kmesh.append(0)
        with open('KPOINTS' , 'r') as fh: line = fh.readlines()
        KPT.append(line[3][:-1])
        os.chdir('../') # back to main directory
        with open(record_file,'a') as fh: fh.write('Finished testing gamma points\n')
    
    # start to test KPOINTS
    while True:    
        if kmesh_value < 0:
            with open(record_file,'a') as fh: fh.write('kmesh value < 0\n')
            break
        # make sure 4 different kpt were tested
        if len(dir_num) < 4:
            wk_dir_num = dir_num[-1] + 1 # current working directory number
            os.mkdir(str(wk_dir_num))
            shutil.copyfile('POSCAR',"%d/POSCAR" % wk_dir_num)
            shutil.copyfile('INCAR', "%d/INCAR" % wk_dir_num)
            os.chdir('./' + str(wk_dir_num))
            set_KPT = 'echo -e "102\n2\n%.2f"| vaspkit' % kmesh_value
            os.system(set_KPT) # create KPOINTS file by using vaspkit
            vasp_cal(incar, structure, set_potcar, vasp_exe, record_file) # run vasp
            outcar_obj = Outcar('OUTCAR')
            E_list.append(outcar_obj.final_energy) ; dir_num.append(wk_dir_num); kmesh.append(kmesh_value)
            with open('KPOINTS' , 'r') as fh: line = fh.readlines()
            KPT.append(line[3][:-1])
            os.chdir('../') # back to main directory
            with open(record_file,'a') as fh: fh.write('Finished testing Kmesh = %f\n' % kmesh_value)
            kmesh_value -= 0.01
            continue
        
        # stop when energy reach the convergenced value
        if len(dir_num) >= 4:
            E_diff = abs(E_list[-1] - E_list[-2])
            if E_diff >= converged_criterion:
                wk_dir_num = dir_num[-1] + 1 # current working directory number
                os.mkdir(str(wk_dir_num))
                shutil.copyfile('POSCAR',"%d/POSCAR" % wk_dir_num)
                shutil.copyfile('INCAR', "%d/INCAR" % wk_dir_num)
                os.chdir('./' + str(wk_dir_num))
                set_KPT = 'echo -e "102\n2\n%.2f"| vaspkit' % kmesh_value
                os.system(set_KPT) # create KPOINTS file by using vaspkit
                vasp_cal(incar, structure, set_potcar, vasp_exe, record_file) # run vasp
                outcar_obj = Outcar('OUTCAR')
                E_list.append(outcar_obj.final_energy) ; dir_num.append(wk_dir_num); kmesh.append(kmesh_value)
                with open('KPOINTS' , 'r') as fh: line = fh.readlines()
                KPT.append(line[3][:-1])
                os.chdir('../') # back to main directory
                with open(record_file,'a') as fh: fh.write('Finished testing Kmesh = %f\n' % kmesh_value)
                kmesh_value -= 0.01
                continue
            else:
                with open(record_file,'a') as fh: fh.write('Finished testing\n'+'='*60)
                return kmesh, E_list, KPT
                
#%%
def plot_fig(kmesh, E_list):
    """
    This function is used to plot the kpt figure.

    Parameters
    ----------
    kmesh : list
        DESCRIPTION. Kmesh-Resolved Value (in Units of 2*PI/Angstrom)
    E_list : list
        DESCRIPTION. Total energy of different k mesh

    Returns
    -------
    None.

    """
    import matplotlib.pyplot as plt
    plt.plot(kmesh, E_list, 'bo')
    plt.xlabel("2*PI/Angstrom")
    plt.ylabel("Total energy (eV)")
    plt.savefig('KPT.png' , dpi = 300)
    
#%%
def vasp_cal(incar,structure,set_potcar,vasp_exe,record_file):
    """
    This func. is used to generate INCAR and POTCAR file in wd. And also do some primary VASP re-calculation
    ### vasp_check func. is required!! ###

    Parameters
    ----------
    incar : pymatgen.io.vasp.inputs.Incar
        DESCRIPTION. pymatgen.io.vasp.inputs.Incar object => use obj.write_file('filename') to write
    structure : pymatgen.core.structure.Structure
        DESCRIPTION. The Structure obj. => Poscar(structure).write_file('filename') write
    set_potcar : str
        DESCRIPTION. The system command for os.system() func. to generate POTCAR
    vasp_exe : str
        DESCRIPTION. The system command for os.system() func. to run VASP
    record_file : str
        DESCRIPTION. The name (Path) of file to record some error out
    """
    import os
    from pymatgen.io.vasp.inputs import Poscar
    from PMG_vasp_methods import vasp_check_err
    
    # 1. generate the input file
    incar.write_file('INCAR') 
    Poscar(structure).write_file('POSCAR') 
    os.system(set_potcar) # Use vaspkit to generate POTCAR file by POSCAR
    
    # 2. run VASP cal.
    os.system(vasp_exe)
    
    # 3. check the calculation successful or not
    ### calculation fail or reach NSW case => backup cal. file & do some change ###
    vasp_check_err(incar,vasp_exe,record_file)  # Check the results, most 3 times repeat
    
#%%
if __name__ == '__main__':
    main()    
