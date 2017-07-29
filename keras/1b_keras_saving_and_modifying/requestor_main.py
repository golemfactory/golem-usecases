import os
import numpy as np
import pickle

from keras_adding_eps.batchmanager import BatchManager
from keras_adding_eps.hash import Hash
from keras_adding_eps.utils import derandom, derandom_callback


from keras_adding_eps import config
from keras.models import load_model


def load_batch(filename):
    with open(filename, "r") as f:
        return pickle.load(f)

def compare_weights(model1, model2):
    weights1 = model1.get_weights()
    weights2 = model2.get_weights()

    for x, y in zip(weights1, weights2):
        # assert(np.equal(x, y).all())
        print(np.equal(x, y).all())

    return all([np.equal(x, y).all()
                for x, y in zip(weights1, weights2)])

def _get_hash_from_name(name):
    return name.split(".")[0].split("_")[0]

def check_model_hash(model, name):
    hash = _get_hash_from_name(name)
    return str(Hash(model)) == hash

# def check_data_hash(data, name):
#     hash = _get_hash_from_name(name)
#     return ... == hash


def find_file_with_ext(ext, dir):
    for file in os.listdir(dir):
        if file.split(".")[-1] == ext:
            return os.path.join(dir, file)

    raise Exception("In dir {} no file with ext {}".format(dir, ext))

if __name__ == "__main__":

    equals = []
    for checkpointdir in os.listdir(config.shared_path):
        path = os.path.join(config.shared_path, checkpointdir)
        startmodel_name, endmodel_name = [find_file_with_ext(ext, path)
                                          for ext in ["begin", "end"]]

        startmodel = load_model(startmodel_name)
        endmodel = load_model(endmodel_name)

        c1 = check_model_hash(startmodel, startmodel_name)
        c2 = check_model_hash(endmodel, endmodel_name)
        derandom()
        batch_manager = BatchManager()
        cur_epoch = int(checkpointdir)
        derandom()
        startmodel.fit_generator(batch_manager,
                                 epochs=cur_epoch+1,
                                 initial_epoch=cur_epoch,
                                 steps_per_epoch=config.STEPS_PER_EPOCH,
                                 callbacks=[derandom_callback])

        equals.append(compare_weights(startmodel, endmodel))

    print(all(equals))