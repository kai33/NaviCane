import subprocess
import re
from multiprocessing import Process
from Queue import Queue, Empty


def execute(command, queue):
    shell_process = subprocess.Popen(VoiceRecognition.POCKETSPHINX_SHELL_CALL,
                                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    while True:
        line = shell_process.stdout.readline()
        if line == '' and shell_process.poll() is not None:
            break
        try:
            m = re.search('^\d{9}:\s?(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NICE|TEN|CANCEL|CONFIRM|\s)\s?$', line)
            recognized_word = m.group(1)
            queue.put(recognized_word)
        except Exception, e:
            queue.put('ERROR')
    queue.put('ERROR')


class VoiceRecognition(object):
    POCKETSPHINX_SHELL_CALL = 'pocketsphinx_continuous -lm dictionary.lm -dict dictionary.dic'

    def __init__(self):
        super(VoiceRecognition, self).__init__()

    def get_command(self, timeout=3):
        shell_process = subprocess.Popen(VoiceRecognition.POCKETSPHINX_SHELL_CALL,
                                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Poll process for new output until finished
        while True:
            line = shell_process.stdout.readline()
            if line == '' and shell_process.poll() is not None:
                break
            try:
                m = re.search('^\d{9}:\s?(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NICE|TEN|CANCEL|CONFIRM|\s)\s?$', line)
                recognized_word = m.group(1)
                return recognized_word
            except Exception, e:
                pass
        return None

if __name__ == '__main__':
    voice_recognition = VoiceRecognition()
    output = voice_recognition.get_command()
    print output
