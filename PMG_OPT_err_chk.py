#!/home/u3130253/.conda/envs/pymatgen_envs/bin/python3.10
"""
Created on Wed Mar  1 13:01:48 2023

@author: Henry, Ayris

Do the NSW != 0 calculation
"""
import os
#%%
def main():
    from pymatgen.core.structure import Structure
    from pymatgen.io.vasp.inputs import Incar
    incar = Incar.from_file('INCAR')
    bk_ver = 0
    structure = Structure.from_file('POSCAR')
    set_potcar = 'echo -e "103\n" | vaspkit'
    Dir = os.listdir()
    if "GAMMA" in Dir:
        vasp_exe = '$VASP_EXECUTION_gam >& log'
    elif "NCL" in Dir:
        vasp_exe = '$VASP_EXECUTION_ncl >& log'
    else:
        vasp_exe = '$VASP_EXECUTION_std >& log'
    record_file = 'record_file'
    with open ('record_file', 'a') as fh: fh.write('='*60+'\n')
    vasp_cal(incar, structure, set_potcar, vasp_exe, record_file, bk_ver)

#%%
def vasp_cal(incar,structure,set_potcar,vasp_exe,record_file, bk_ver):
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
    
    # 1. generate the input file
    incar.write_file('INCAR') 
    Poscar(structure).write_file('POSCAR') 
    os.system(set_potcar) # Use vaspkit to generate POTCAR file by POSCAR
    
    # 2. run VASP cal.
    os.system(vasp_exe)
    
    # 3. check the calculation successful or not
    ### calculation fail or reach NSW case => backup cal. file & do some change ###
    vasp_check_err(incar,vasp_exe,record_file, bk_ver)  # Check the results, most 3 times repeat
    vasp_reach_nsw(incar, vasp_exe, record_file, bk_ver)
#%%      
def vasp_check_err(incar,vasp_exe,record_file, bk_ver):
    ### No directory name ["INCAR", "POSCAR", "CONTCAR", "XDATCAR", "OSZICAR", "OUTCAR", "log"] + "_v*"
    import os
    import copy
    import shutil
    
    with open("OUTCAR",'r') as f: outcar = f.readlines()
    
    ### calculation fail case => backup cal. file & do some change ###
    backup_file_list = ["INCAR", "POSCAR", "CONTCAR", "XDATCAR", "OSZICAR", "OUTCAR", "log"]
    if "User time (sec)" not in outcar[-10]:
        for i in range(3):   # i+1 = the number of re-calculation and for label of backup
            ### read the OUTCAR and log file again ###    
            with open("OUTCAR",'r') as f: outcar = f.readlines()
            with open('log','r') as f: LOG = f.readlines()
            if "User time (sec)" in outcar[-10]: break
            
            ### find the number of backup version in this dir (ex. POSCAR_v2 -> version '2')
            ### version start from v0, v1, v2, ...
            for file in os.listdir():
                if 'POSCAR_v' in file: bk_ver += 1
                
                
            ### BRMIX error checker => stop code ###
            is_BRMIX = False
            for line in LOG:
                if "BRMIX: very serious problems" in line: 
                    is_BRMIX = True
            
            if is_BRMIX == True:
                # record the error
                with open(record_file,'a') as f: f.write("BRMIX Error in %s for %d ver.! Leaving this cal."
                                                         %( os.getcwd() , i ) + '\n')
                break  # leaving this directory and do other cal.
                
            ### ZHEGV error checker => permanently override 'ALGO' in incar ###
            is_ZHEGV = False
            for line in outcar:
                if "ZHEGV" in line: 
                    is_ZHEGV = True
            
            if is_ZHEGV == True:
                # backup and record
                for file in backup_file_list: shutil.copyfile(file,file + '_v%d' % bk_ver)
                with open(record_file,'a') as f: f.write("ZHEGV Error in %s for %d ver."%(os.getcwd(),bk_ver) + '\n')
                    
                # operation will override the 'ALGO' tag for later cal. permanantly
                if ('ALGO' not in incar.keys()) or (incar['ALGO'][0].upper()=='N'):
                    incar['ALGO'] = 'Fast'
                    incar.write_file('INCAR')
                    shutil.copyfile("CONTCAR","POSCAR")
                    os.system(vasp_exe)
                    continue
                elif (incar['ALGO'][0].upper()=='F') or (incar['ALGO'][0].upper()=='V'):
                    incar['ALGO'] = 'Normal'
                    incar.write_file('INCAR')
                    shutil.copyfile("CONTCAR","POSCAR")
                    os.system(vasp_exe)
                    continue
                
            ### ZBRENT error checker => no permanent overriding ###
            if "ZBRENT: fatal error" in LOG[-3]:
                # backup and record
                for file in backup_file_list: shutil.copyfile(file,file + '_v%d' % bk_ver)
                with open(record_file,'a') as f: f.write("ZBRENT Error in %s for %d ver."%(os.getcwd(),bk_ver) + '\n')
                
                # operation
                new_incar = copy.deepcopy(incar)   # don't overwrite the IBRION tag for later cal.
                new_incar['IBRION'] = 1  # set quasi-newton
                new_incar.write_file('INCAR')
                shutil.copyfile("CONTCAR","POSCAR")
                os.system(vasp_exe)
                continue
    
            ### PMPI_Allreduce error checker => no permanent overriding ###
            if "PMPI_Allreduce" in LOG[-1]:
                # backup and record
                for file in backup_file_list: shutil.copyfile(file,file + '_v%d' % bk_ver)
                with open(record_file,'a') as f: f.write("PMPI_Allreduce Error in %s for %d ver."%(os.getcwd(),bk_ver) + '\n')
                
                # operation
                new_incar = copy.deepcopy(incar)
                new_incar['AMIX'] = 0.2  # suggested by https://www.vasp.at/wiki/index.php/AMIX_MAG
                new_incar['BMIX'] = 0.0001
                new_incar['AMIX_MAG'] = 0.8
                new_incar['BMIX_MAG'] = 0.0001
                new_incar.write_file('INCAR')
                shutil.copyfile("CONTCAR","POSCAR")
                os.system(vasp_exe)
                continue
#%%
def vasp_reach_nsw(incar,vasp_exe,record_file, bk_ver):
    import shutil
    import os
    import copy

    backup_file_list = ["INCAR", "POSCAR", "CONTCAR", "XDATCAR", "OSZICAR", "OUTCAR", "log"]
    
    if bk_ver < 3:  
        ### reach NSW => no permanent overwriding (This check should be last one) ###
        ### if oszicar[-1].split()[0] not 'int' => no final ionic loop => new checker is required! ###
        with open("OSZICAR",'r') as f: oszicar = f.readlines()
        if (int(oszicar[-1].split()[0]) == incar['NSW']) and (incar['NSW'] > 1):
            ### find the number of backup version in this dir (ex. POSCAR_v2 -> version '2')
            ### version start from v0, v1, v2, ...
            bk_ver = 0
            for file in os.listdir():
                if 'POSCAR_v' in file: bk_ver += 1
            for file in backup_file_list: shutil.copyfile(file,file + '_v%d' % bk_ver)
            with open(record_file,'a') as f: f.write("Reach NSW in %s for %d ver."%(os.getcwd(),bk_ver) + '\n')
                    
            # operation
            new_incar = copy.deepcopy(incar)
            new_incar['ISTART'] = 1 # turn on ISTART to read the WAVECAR
            incar.write_file('INCAR')
            shutil.copyfile("CONTCAR","POSCAR") # mv CONTCAR POSCAR
            os.system(vasp_exe)
            vasp_reach_nsw(incar, vasp_exe, record_file, bk_ver)
        # if NSW didn't reach the critira --> check err
        else:
            vasp_check_err(incar, vasp_exe, record_file, bk_ver)
            
#%%
if __name__ == "__main__":
    main()
