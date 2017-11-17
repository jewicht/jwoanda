from abc import ABCMeta, abstractmethod
from six import with_metaclass

class BaseInterface(with_metaclass(ABCMeta)):

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def setprice(self, name, b, a):
        pass
