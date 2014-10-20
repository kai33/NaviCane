import subprocess
import re


def is_connected():
    shell_process = subprocess.Popen('exec ping www.google.com',
                                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    line = shell_process.stdout.readline()
    if re.search('^ping: unknown host', line):
        shell_process.kill()
        return False
    else:
        shell_process.kill()
        return True
