import abc

class iExecute(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, comands:list, *args)->dict:
        pass