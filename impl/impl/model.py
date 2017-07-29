import itertools
import os
import dill as pickle

import numpy as np
from torch import nn, torch, from_numpy
from torch.autograd import Variable

from impl import config
from impl.batchmanager import IrisBatchManager
from impl.box import SimpleBlackBox
from impl.hash import PyTorchHash
from impl.net import Net
from impl.utils import derandom


class Model(object):
    def __init__(self, input_size: int, hidden_size: int, num_classes: int, learning_rate: int):
        self.kwargs = {}
        self.kwargs["input_size"] = input_size
        self.kwargs["hidden_size"] = hidden_size
        self.kwargs["num_classes"] = num_classes
        self.kwargs["learning_rate"] = learning_rate

        self.net = Net(input_size=input_size,
                       hidden_size=hidden_size,
                       num_classes=num_classes)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(self.net.parameters(), lr=learning_rate)

    def run_one_batch(self, x: np.ndarray, y: np.ndarray):
        derandom()
        x = Variable(from_numpy(x).view(config.BATCH_SIZE, -1).type(torch.FloatTensor))

        y = np.argmax(y, axis=1)
        y = Variable(from_numpy(y).view(config.BATCH_SIZE).type(torch.LongTensor))

        self.optimizer.zero_grad()
        outputs = self.net(x)
        loss = self.criterion(outputs, y)
        loss.backward()
        self.optimizer.step()

    def get_kwargs(self):
        return self.kwargs


class ModelSerializer():
    def __init__(self, model: Model, shared_path: str, save_model_as_dict):
        self.model = model
        self.save_model_as_dict = save_model_as_dict
        self.shared_path = shared_path

        if not os.path.exists(self.shared_path):
            os.makedirs(self.shared_path)

    def _get_current_model_hash(self):
        return self.get_model_hash(self.model)

    @staticmethod
    def get_model_hash(model):
        return PyTorchHash(model.net)

    def _get_path_to_save(self, epoch: int, ext):
        # dir = "{}_{}".format(str(self.epoch), str(batch))
        dir = str(epoch)
        dir = os.path.join(self.shared_path, dir)

        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = str(self._get_current_model_hash()) + "." + ext
        return os.path.join(dir, filename)

    def save(self, epoch, ext):
        filepath = self._get_path_to_save(epoch, ext=ext)

        if self.save_model_as_dict:
            state_dict = {
                "epoch": epoch,
                # "minibatch": self.minibatch_num,
                # "arch": config.ARCH,
                "network_state_dict": self.model.net.state_dict(),
                "optimizer_state_dict": self.model.optimizer.state_dict(),
                "model_kwargs": self.model.get_kwargs()
            }
            torch.save(state_dict, filepath)
        else:
            with open(filepath, "w") as f:
                pickle.dump(self.model, f)

    @staticmethod
    def load(path):
        checkpoint = torch.load(path)
        model_kwargs = checkpoint["model_kwargs"]
        model = Model(**model_kwargs)
        model.net.load_state_dict(checkpoint['network_state_dict'])
        model.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        # start_epoch = checkpoint['epoch']

        return model


class ModelRunner(object):
    def __init__(self, shared_path: str, probability, save_model_as_dict=True, verbose=False):

        self.black_box = SimpleBlackBox(probability)
        self.batch_manager = IrisBatchManager()

        self.model = Model(self.batch_manager.get_input_size(),
                           config.HIDDEN_SIZE,
                           config.NUM_CLASSES,
                           config.LEARNING_RATE)

        self.serializer = ModelSerializer(self.model, shared_path, save_model_as_dict)

        self.should_save = False

    def run_full_training(self):
        for epoch in range(config.NUM_EPOCHS):
            self.on_epoch_begin(epoch)

            for i, (x, y) in enumerate(itertools.islice(self.batch_manager, config.STEPS_PER_EPOCH)):
                self.model.run_one_batch(x, y)

            self.on_epoch_end(epoch)

    def on_epoch_end(self, epoch: int):
        if self.should_save:
            self.should_save = False
            self.serializer.save(epoch, "end")

    def on_epoch_begin(self, epoch: int):
        box_decision = self.black_box.decide(self.serializer._get_current_model_hash())
        if box_decision:
            self.should_save = True
            self.serializer.save(epoch, "begin")

            # self.batch_generator.save()

