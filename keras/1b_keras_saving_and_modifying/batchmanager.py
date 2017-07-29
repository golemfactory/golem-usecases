import pickle

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from keras_adding_eps import config
from keras_adding_eps.utils import derandom


class BatchManager(object):
    def __init__(self, datafile="/home/jacek/datasets/IRIS.csv"):
        self.datafile = datafile

        data = pd.read_csv(datafile, header=None)

        derandom()
        data = data.reindex(np.random.permutation(data.index))

        y = pd.get_dummies(data[8]).values
        x = data[list(range(7))]
        x = ((x - x.mean()) / (x.max() - x.min())).values

        derandom()
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=config.TEST_SIZE, random_state=42)

        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.current_index = -20

    def __iter__(self):
        return self

    def __next__(self):
        # TODO very ugly
        # in the iris dataset there are 100 samples, so 80 for training
        # this generator will loop over them by 20

        # It may not work in this order
        self.current_index = (self.current_index + config.BATCH_SIZE) % config.IRIS_SIZE

        return (self.x_train[self.current_index: self.current_index + config.BATCH_SIZE],
               self.y_train[self.current_index: self.current_index + config.BATCH_SIZE])

    def save(self, batch_num, filepath):
        print("aaaa", batch_num, self.current_index)
        # assert(batch_num == self.current_index) # TODO why it doesn't work?

        batch = (self.x_train[self.current_index: self.current_index + config.BATCH_SIZE],
                 self.y_train[self.current_index: self.current_index + config.BATCH_SIZE])

        with open(filepath, "wb") as f:
            pickle.dump(batch, f)

    def get_input_size(self):
        return self.x_train[0].size

    def get_full_training_set(self):
        return self.x_train, self.y_train