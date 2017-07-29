from hashlib import sha3_256

from keras.models import Sequential
from torch import nn


class Hash(object):

    def __init__(self, value):
        self.value = self._compute_hash(value)

    def last_bytes_int(self, size: int) -> int:
        return self._int_from_bytes(self.value[:size])

    def __repr__(self):
        return str(self.value.hex())

    def _compute_hash(self, value) -> bytes:
        # return bytes(sha3_256(pickle.dumps(value))) # non-determinitic
        return bytes(sha3_256(hash(value))) # python hash() is very short - only 4 bytes!

    # from https://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3
    @staticmethod
    def _int_to_bytes(x: int):
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')

    @staticmethod
    def _int_from_bytes(xbytes: bytes):
        return int.from_bytes(xbytes, 'big')


class PyTorchHash(Hash):

    def __init__(self, value: nn.Module):
        super().__init__(value)

    def _compute_hash(self, value: nn.Module):
        # for pytorch
        # this is copying data every time, in function tobytes()
        return sha3_256("".join([str(v.data.numpy()) for v in value.parameters()]).encode()).digest()


class KerasHash(Hash):

    def __init__(self, value: Sequential):
        super().__init__(value)

    def _compute_hash(self, value):
        # for keras
        # this is copying data every time, in function tobytes()
        return sha3_256("".join([str(hash(c.tobytes())) for v in value.layers for c in v.get_weights()]).encode()).digest()
