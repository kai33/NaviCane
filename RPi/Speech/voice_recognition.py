import subprocess
import re
import os
from espeak_api import VoiceOutput


class VoiceRecognition(object):
    lm_file_path = os.path.dirname(os.path.abspath(__file__)) + '/dictionary.lm'
    dic_file_path = os.path.dirname(os.path.abspath(__file__)) + '/dictionary.dic'
    POCKETSPHINX_SHELL_CALL = 'pocketsphinx_continuous -lm ' + lm_file_path + ' -dict ' + dic_file_path
    REGEX_MATCH_STRING = '^\d{9}:\s?((?:(?:ZERO|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|CANCEL|CONFIRM)\s)+)\s?$'
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
