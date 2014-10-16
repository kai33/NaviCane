import subprocess
import threading


class VoiceOutput(object):
    def __init__(self):
        super(VoiceOutput, self).__init__()
        self._process = None

    def speak(self, text, timeout=None):
        def target():
            self._process = subprocess.Popen('espeak -v en-uk -s 130 --stdout "' + text + '" | aplay ', shell=True)
            self._process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self._process.terminate()
            thread.join()
        return self._process.returncode

if __name__ == '__main__':
    text = "Testing espeak with python script"
    output = VoiceOutput()
    output.speak(text, None)
    output.speak(text, timeout=10)
