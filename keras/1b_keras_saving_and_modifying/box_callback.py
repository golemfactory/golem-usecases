from keras.callbacks import Callback
from keras_adding_eps.utils import derandom
import os

from keras_adding_eps.box import BlackBox
from keras_adding_eps.hash import Hash
from keras_adding_eps.batchmanager import BatchManager


class BlackBoxCallback(Callback):
    """After every batch, check if BlackBox decided
    to save the model, and if that's the case, save
    it in the filename location

    # Arguments
        filepath: string, path to save the model file.
        verbose: verbosity mode, 0 or 1.
        save_weights_only: if True, then only the model's weights will be
            saved (`model.save_weights(filepath)`), else the full model
            is saved (`model.save(filepath)`).
        black_box: Black box deciding if the state should be saved.
    """

    def __init__(self, filepath: str, black_box: BlackBox, batch_generator: BatchManager, verbose=0, save_weights_only=False):
        super().__init__()
        self.verbose = verbose
        self.black_box = black_box
        self.batch_generator = batch_generator
        self.save_weights_only = save_weights_only
        self.shared_dir = filepath

        self.should_save = False
        self.should_save2 = False

        if not os.path.exists(self.shared_dir):
            os.makedirs(self.shared_dir)
        else:
            # raise Exception("Path already exists")
            pass

    def _get_current_model_hash(self):
        return Hash(self.model)

    def _get_path_to_save(self, epoch: int, ext):
        # dir = "{}_{}".format(str(self.epoch), str(batch))
        dir = str(epoch)
        dir = os.path.join(self.shared_dir, dir)

        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = str(self._get_current_model_hash()) + "." + ext
        return os.path.join(dir, filename)

    def on_epoch_end(self, epoch: int, logs=None):

        # if self.epochs_since_last_save >= fixed_N:
            # call AdvancedBlackbox

        if self.should_save:
            self.should_save = False

            filepath = self._get_path_to_save(epoch, ext="end") # epoch-1 is crucial!

            # if self.save_weights_only:
            #     self.model.save_weights(filepath, overwrite=True)
            # else:
            self.model.save(filepath, overwrite=True)

        # box_decision = self.black_box.decide(self._get_current_model_hash())
        # if box_decision:
        #     self.should_save = True
        #
        #     filepath = self._get_path_to_save(epoch, ext="begin")
        #
        #     # if self.save_weights_only:
        #     #     self.model.save_weights(filepath, overwrite=True)
        #     # else:
        #     self.model.save(filepath, overwrite=True)
        #
        #     # self.batch_generator.save()

    def on_epoch_begin(self, epoch: int, logs=None):

        # if self.epochs_since_last_save >= fixed_N:
            # call AdvancedBlackbox

        # if self.should_save2:
        #     self.should_save2 = False
        #
        #     filepath = self._get_path_to_save(epoch-1, ext="end2") # epoch-1 is crucial!
        #
        #     # if self.save_weights_only:
        #     #     self.model.save_weights(filepath, overwrite=True)
        #     # else:
        #     self.model.save(filepath, overwrite=True)


        box_decision = self.black_box.decide(self._get_current_model_hash())
        if box_decision:
            self.should_save = True

            filepath = self._get_path_to_save(epoch, ext="begin")

            # if self.save_weights_only:
            #     self.model.save_weights(filepath, overwrite=True)
            # else:
            self.model.save(filepath, overwrite=True)

            # self.batch_generator.save()