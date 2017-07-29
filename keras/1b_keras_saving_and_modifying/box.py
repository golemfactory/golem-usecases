import random
from .hash import Hash
from abc import abstractmethod, ABCMeta


class BlackBox(metaclass=ABCMeta):
    LAST_BYTES_NUM = 1 # max value 256

    @abstractmethod
    def decide(self, hash: Hash) -> bool:
        pass


class SimpleBlackBox(BlackBox):
    LAST_BYTES_NUM = 1 # max value 256

    def __init__(self, probability: float, seed=42):
        self.seed = seed # TODO do something with that seed
        self.history = []
        self.probability = probability # probability of BlackBox saying 'save'
        self.difficulty = int(2**(8*self.LAST_BYTES_NUM) * self.probability)

    def decide(self, hash: Hash):
        self.history.append(hash)
        if hash.last_bytes_int(size=self.LAST_BYTES_NUM) <= self.difficulty:
            return True
        return False
