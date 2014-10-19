import subprocess
import re
from multiprocessing import Process
from Queue import Queue, Empty
from espeak_api import VoiceOutput


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
            queue.put(str(e))
    queue.put('ERROR')


class VoiceRecognition(object):
    POCKETSPHINX_SHELL_CALL = 'pocketsphinx_continuous -lm dictionary.lm -dict dictionary.dic'
    REGEX_MATCH_STRING = '^\d{9}:\s?(((:?ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|CANCEL|CONFIRM)\s))\s?$'
    REGEX_MATCH_READY = '^READY....\s?$'

    def __init__(self):
        super(VoiceRecognition, self).__init__()
        self._voice_out = VoiceOutput()

    def get_command(self, timeout=3):
        shell_process = subprocess.Popen('exec ' + VoiceRecognition.POCKETSPHINX_SHELL_CALL,
                                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Poll process for new output until finished
        while True:
            line = shell_process.stdout.readline()
            if line == '' and shell_process.poll() is not None:
                break
            try:
                m = re.search(VoiceRecognition.REGEX_MATCH_STRING, line)
                r = re.search(VoiceRecognition.REGEX_MATCH_READY, line)
                if m:
                    recognized_word = m.group(1)
                    shell_process.kill()
                    return recognized_word
                elif r:
                    self._voice_out.speak('ready')
                else:
                    continue
            except Exception, e:
                print(str(e))
        shell_process.kill()
        return None

if __name__ == '__main__':
    voice_recognition = VoiceRecognition()
    output = voice_recognition.get_command()
    print output
