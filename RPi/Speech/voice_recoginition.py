import subprocess
import sys
from multiprocessing import Process
from Queue import Queue, Empty


def execute(command, queue):
    shell_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    while True:
        line = shell_process.stdout.readline()
        if line == '' and shell_process.poll() is not None:
            break
        sys.stdout.write(line)
        sys.stdout.flush()
        queue.put(line)


class VoiceRecognition(object):
    POCKETSPHINX_SHELL_CALL = 'pocketsphinx_continuous -lm dictionary.lm -dict dictionary.dic'

    def __init__(self):
        super(VoiceRecognition, self).__init__()
        self._queue = Queue()
        self._worker = Process(target=execute,
                               args=(VoiceRecognition.POCKETSPHINX_SHELL_CALL, self._queue))
        self._worker.daemon = True
        self._worker.start()

    def get_command(self, timeout=None):
        try:
            return self._queue.get(block=timeout is not None, timeout=timeout)
        except Empty:
            return None

if __name__ == '__main__':
    voice_recognition = VoiceRecognition()
    while True:
        output = voice_recognition.get_command()
        # print output
