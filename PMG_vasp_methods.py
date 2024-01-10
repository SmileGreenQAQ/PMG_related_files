#!/home/u3130253/.conda/envs/pymatgen_envs/bin/python3.10
"""
Created on Tue Mar  7 11:05:06 2023

@author: Henry, Ayris

Methods for VASP calculation are recorded here!
"""

#%%      
def vasp_check_err(incar,vasp_exe,record_file = 'record_file'):
    ### No directory name ["INCAR", "POSCAR", "CONTCAR", "XDATCAR", "OSZICAR", "OUTCAR", "log"] + "_v*"
    import os
    import copy
    import shutil
    
    with open("OUTCAR",'r') as f: outcar = f.readlines()
    bk_ver = 1
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
