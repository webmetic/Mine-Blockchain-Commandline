import os
import subprocess

path = os.path.abspath(os.getcwd())
Batfile_path = path + "\Mine_Bat_file.bat"

if not os.path.isfile(Batfile_path):
    Backendfile_path = path + "\Mine_backend.py"
    Batfile = open(r'%s' % Batfile_path, 'w+')
    Batfile.write("@echo off\ntitle Mine Command Line\npython " + Backendfile_path + "\n pause")
    
    Batfile.close()

subprocess.call([r'%s' % Batfile_path])
