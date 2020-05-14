#!/usr/bin/env python
# Runs a command ingesting environment variables
# Returns return code, stdout

import os
import subprocess
import sys

def run_command(a_command, env):
    try:
        for k,v in env.items():
            os.environ[k] = v 
        the_shell_cmd = subprocess.Popen(a_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        the_stdout, the_stderr = the_shell_cmd.communicate()
        the_return_code = the_shell_cmd.returncode
        if the_return_code != 0:
            print("RC : " + str(the_return_code))
            print("Output : " + str(the_stdout))
        return the_return_code, the_stdout
    except Exception as e:
        raise e
