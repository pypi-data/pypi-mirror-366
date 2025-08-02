from pyinno_setup import runit
from pathlib import Path

"""
this is used for calling embedded innosetuip compiler exe file,(required files are in libs folder)
it will give iss file as input and output is exe file,
output folder canbe changed all other settings are controlled by contents of iss file
to generate iss file try my other module 'pyinno_gen'
if somehow embeded exe is missing then you can change module attribute EXE_PATH to use your own

author: github.com/its-me-abi
date : 12/7/2025
"""

current_folder = Path(__file__).parent.resolve()
EXE_PATH = Path(current_folder) / "libs/Inno6/ISCC.exe"

def build( input_iss_file_path, outfolder = "" ,extra_commands =[]):
    "if outfolder isa empty then exe file willbe generated in subfolder of code"
    if not EXE_PATH.exists():
        print("embedded exe file not found,probably script or exe files moved cwd = ", current_folder)
        return

    command = [EXE_PATH]
    if outfolder:
        command += [f"/O{outfolder}" ]
    if extra_commands:
        command += extra_commands
    if input_iss_file_path:
        command += [ input_iss_file_path]

    if runit.run_subprocess(command) == 0:
       return True


if __name__ == "__main__":

    input_path = Path(current_folder) / "data/template.iss"
    output_folder = "output"
    print("### building exe " ,input_path )
    if build (input_path,output_folder):
        print("### successfully built ")
    else:
        print("### build failed ")