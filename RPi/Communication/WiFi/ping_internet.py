import subprocess
import re


def is_connected():
    shell_process = subprocess.Popen('ping www.google.com',
                                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    line = shell_process.stdout.readline()
    if re.search('^ping: unknown host www.google.com', line):
        return False
    else:
        return True
