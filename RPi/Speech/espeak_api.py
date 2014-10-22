import subprocess


class VoiceOutput(object):
    def __init__(self):
        super(VoiceOutput, self).__init__()
        self._process = None

    def speak(self, text):
        self._process = subprocess.Popen('espeak -v en-us -s 160 --stdout "' + text + '" | aplay ',
                                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self._process.wait()
        return self._process.returncode

if __name__ == '__main__':
    text = "Testing espeak with python script"
    output = VoiceOutput()
    print output.speak(text)
    print output.speak(text)
