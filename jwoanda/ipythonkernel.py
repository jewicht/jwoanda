import threading

import IPython
#import mock


class IPythonKernelThread(threading.Thread):

    def __init__(self):
        super(IPythonKernelThread, self).__init__()

    def run(self):
#        with mock.patch('signal.signal'):
        IPython.embed_kernel()
