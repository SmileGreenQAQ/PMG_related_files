#!/home/u3130253/.conda/envs/pymatgen_envs/bin/python3.10
"""
Created on Fri Sep 15 13:34:48 2023

@author: Hsu-Chen CHENG (Ayris)

This code can help you do the vasp relaxation and get a finer total energy.
Total N computations will be done, the convergence criteria will become higher.
To activate code in HPC, please put it into the job_script and submit it.
This code requires pymatgen.
To use this code, INCARs, KPOINTSs, and POSCAR should be put in the current directory. POTCAR is optional.
INCAR formats: INCAR_1, INCAR_2, INCAR_3...
KPOINTS formats: KPOINTS_1, KPOINTS_2, ...
Reminder: Different users should have their own python environment, please change the 1st line before you use.
"""

#%%
def main():
    import os
    import time
    start = time.time()
    set_potcar = 'echo -e "103\n" | vaspkit'
    vasp_err_chk = 'PMG_OPT_err_chk.py'
    record_file = 'record_file'
    with open ('record_file', 'a') as fh: fh.write('='*60+'\n')
    if 'POTCAR' not in os.listdir():
        os.system(set_potcar)
    incar_number = 0
    step = 1
    for i in os.listdir():
        if "INCAR_" in i:
            incar_number += 1
    for i in range(incar_number):
        opt(step, vasp_err_chk, record_file)
        step += 1
    os.remove("WAVECAR")
    os.remove("CHGCAR")
    end = time.time()
    time_hr = (end - start) / 3600
    with open('record_file', 'a') as fh:
        fh.write("Elapsed time: %3f hr" % (time_hr))
    
#%%
def opt(step, vasp_err_chk, record_file):
    import shutil
    import os
    step_name = 'step_'+str(step)
    os.mkdir(step_name)
    shutil.copy("./INCAR_" + str(step), step_name + "/INCAR")
    shutil.copy("./KPOINTS_" + str(step), step_name + "/KPOINTS")
    shutil.copy("POTCAR", step_name + "/POTCAR")
    if "VASPTYPE" in os.listdir():
        with open("VASPTYPE",'r') as fh:
            lines = fh.readlines()
        vasptype = lines[step-1][:-1]
        if (step > 1):  # > step_1
            if (vasptype == lines[step-2][:-1]) and (vasptype == "vasp_gam"):
                if "CHGCAR" in os.listdir():
                    shutil.move("CHGCAR", step_name + "/CHGCAR")
                if "WAVECAR" in os.listdir():
                    shutil.move("WAVECAR", step_name + "/WAVECAR")
                shutil.copy("CONTCAR_step" + str(step-1), step_name + "/POSCAR")
                os.chdir(step_name)
                os.system('touch GAMMA')
            elif (vasptype == lines[step-2][:-1]) and (vasptype == "vasp_ncl"):
                if "CHGCAR" in os.listdir():
                    shutil.move("CHGCAR", step_name + "/CHGCAR")
                if "WAVECAR" in os.listdir():
                    shutil.move("WAVECAR", step_name + "/WAVECAR")
                shutil.copy("CONTCAR_step" + str(step-1), step_name + "/POSCAR")
                os.chdir(step_name)
                os.system('touch NCL')
            elif (vasptype == lines[step-2][:-1]) and (vasptype == "vasp_std"):
                if "CHGCAR" in os.listdir():
                    shutil.move("CHGCAR", step_name + "/CHGCAR")
                if "WAVECAR" in os.listdir():
                    shutil.move("WAVECAR", step_name + "/WAVECAR")
                shutil.copy("CONTCAR_step" + str(step-1), step_name + "/POSCAR")
                os.chdir(step_name)
            elif vasptype != lines[step-2]:
                if "CHGCAR" in os.listdir():
                    os.remove("CHGCAR")
                if "WAVECAR" in os.listdir():
                    os.remove("WAVECAR")
                shutil.copy("CONTCAR_step" + str(step-1), step_name + "/POSCAR")
                os.chdir(step_name)
            os.system(vasp_err_chk)
            shutil.copy("CONTCAR", "../CONTCAR_step" + str(step))
            shutil.move("WAVECAR", "../")
            shutil.move("CHGCAR", "../")
            os.chdir("../")
            with open (record_file, 'a') as fh: 
                fh.write('Finished step ' + str(step) + '\n')

        else:  # step_1 case
            if vasptype == "vasp_gam":
                shutil.copy("POSCAR", step_name + "/POSCAR")
                os.chdir(step_name)
                os.system('touch GAMMA')
                os.system(vasp_err_chk)
            elif vasptype == "vasp_ncl":
                shutil.copy("POSCAR", step_name + "/POSCAR")
                os.chdir(step_name)
                os.system('touch NCL')
                os.system(vasp_err_chk)
            else:
                shutil.copy("POSCAR", step_name + "/POSCAR")
                os.chdir(step_name)
                os.system(vasp_err_chk)
            shutil.copy("CONTCAR", "../CONTCAR_step" + str(step))
            shutil.move("WAVECAR", "../")
            shutil.move("CHGCAR", "../")
            os.chdir("../")
            with open (record_file, 'a') as fh: fh.write('Finished step ' + str(step) + '\n')
    else:
        if "CHGCAR" in os.listdir():
            shutil.move("CHGCAR", step_name + "/CHGCAR")
        if "WAVECAR" in os.listdir():
            shutil.move("WAVECAR", step_name + "/WAVECAR")
        if step == 1:
            shutil.copy("POSCAR", step_name + "/POSCAR")
        if step > 1:
            shutil.copy("CONTCAR_step" + str(step-1), step_name + "/POSCAR")
        os.chdir(step_name)
        os.system(vasp_err_chk)
        shutil.copy("CONTCAR", "../CONTCAR_step" + str(step))
        shutil.move("WAVECAR", "../")
        shutil.move("CHGCAR", "../")
        os.chdir("../")
        with open (record_file, 'a') as fh: fh.write('Finished step ' + str(step) + '\n')

#%%
if __name__ == "__main__":
    main()
