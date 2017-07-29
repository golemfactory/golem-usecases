from hashlib import sha3_256
import dill as pickle # TODO pickle can be not reliable (it doesn't keep the dictionary order for example), maybe use bencode or something...

# from https://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3
from keras.models import Sequential


def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(xbytes):
    return int.from_bytes(xbytes, 'big')


class Hash(object):
    def __init__(self, value: Sequential):
        # self.value: bytes = sha3_256(value.__hash__()) # hash is very short! only 4 bytes TODO change that!
        # self.value: bytes = sha3_256(pickle.dumps(value)) # non-determinitic
        self.value: bytes = sha3_256("".join([str(hash(c.tobytes())) for v in value.layers for c in v.get_weights()]).encode()).digest() # this is copying data every time

    # If type of value will be Model, I can use weights for hash
        # assert(type(value) == keras.model.Model
        # self.value: bytes = sha3_256(model.weights)

    def last_bytes_int(self, size: int):
        return int_from_bytes(self.value[:size])

    def __repr__(self):
        return str(self.value.hex())