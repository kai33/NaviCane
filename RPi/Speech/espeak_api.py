#!/usr/bin/env python
import subprocess
import threading


class VoiceOutput(object):
    def __init__(self, text):
        self.text = text
        self.process = None

    def voiceOutput(self, timeout=None):
        def target():
            self.process = subprocess.Popen('espeak -v en-uk -s 130 --stdout "' + text + '" | aplay ', shell=True)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode

if __name__ == '__main__':
    text = "Testing espeak with python script"
    output = VoiceOutput(text)
    output.voiceOutput(None)
    output.voiceOutput(timeout=10)
