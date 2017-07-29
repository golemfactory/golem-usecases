import numpy as np
from .utils import derandom, derandom_callback

from keras.layers import Dense, Dropout
from keras.activations import relu, softmax
from keras.models import Sequential
from keras.optimizers import Adam
from keras.losses import categorical_crossentropy

from keras_adding_eps import config
from keras_adding_eps.batchmanager import BatchManager
from keras_adding_eps.box import SimpleBlackBox
from keras_adding_eps.box_callback import BlackBoxCallback

class NeuralNet(object):

    def __init__(self, black_box_callback: BlackBoxCallback, batch_manager: BatchManager):
        self.model = Sequential([Dense(7500, activation=relu, input_shape=[batch_manager.get_input_size()]),
                                 Dropout(0.5),
                                 Dense(3, activation=softmax)])
        self.model.compile(Adam(), categorical_crossentropy, metrics=["accuracy"])
        self.black_box_callback = black_box_callback
        self.batch_manager = batch_manager

    def run(self):
        for epoch in range(10):
            derandom()
            self.model.fit_generator(self.batch_manager,
                                     steps_per_epoch=config.STEPS_PER_EPOCH,
                                     epochs=epoch+1,
                                     initial_epoch=epoch,
                                     callbacks=[derandom_callback, self.black_box_callback])
        # from sklearn.model_selection import cross_val_score
        # from sklearn.metrics import accuracy_score
        # model.test_on_batch(x_test, y_test)

        # for layer in model.layers:
        #     weights = layer.get_weights() # list of numpy arrays
        #     print(len(weights))


class NeuralNetRunner(object):

    def __init__(self, filepath, probability, verbose, save_weights_only):
        self.black_box = SimpleBlackBox(probability)
        self.batch_mangaer = BatchManager()

        self.black_box_callback = BlackBoxCallback(filepath,
                                                   self.black_box,
                                                   self.batch_mangaer,
                                                   verbose)

        self.network = NeuralNet(self.black_box_callback, self.batch_mangaer)

    def run(self):
        self.network.run()