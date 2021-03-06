import itertools
import os

import numpy as np
from typing import Type, Tuple

from impl import config, utils
from impl.batchmanager import IrisBatchManager
from impl.model import ModelSerializer, IrisSimpleModel


class Verificator(object):
    def __init__(self, out_dir, expected_samples_num: Tuple[float, float]):
        self.out_dir = out_dir
        self.expected_samples_num, self.confidence_interval = expected_samples_num

    def verificate(self):

        serializer: Type[ModelSerializer] = ModelSerializer
        model: Type[IrisSimpleModel] = IrisSimpleModel

        files = os.listdir(self.out_dir)

        # we could care about number of samples only if it was smaller than what we expected
        # but it is always worth to have some additional sanity check
        if len(files) - self.expected_samples_num > self.confidence_interval:
            print("Wrong number of files in {}. Expected {} +- {} (with 95% confidence interval), got {}".format(
                self.out_dir, self.expected_samples_num, self.confidence_interval, len(files)
            ))
            return False

        for checkpointdir in files:
            # loading models
            path = os.path.join(config.SHARED_PATH, checkpointdir)
            startmodel_name, endmodel_name = [self._find_file_with_ext(ext, path)
                                              for ext in ["begin", "end"]]

            startmodel = serializer.load(startmodel_name)
            endmodel = serializer.load(endmodel_name)

            # hashes checking
            htrue = str(startmodel.get_hash())
            hname = self._get_hash_from_name(startmodel_name)
            if hname != htrue:
                print("Wrong start model hash\n "
                      "Expecting {}"
                      "Got {}".format(hname, htrue))
                return False

            htrue = str(endmodel.get_hash())
            hname = self._get_hash_from_name(endmodel_name)
            if hname != htrue:
                print("Wrong start model hash\n "
                      "Expecting {}"
                      "Got {}".format(hname, htrue))
                return False

            batch_manager = IrisBatchManager()

            # one epoch of training
            for i, (x, y) in enumerate(itertools.islice(batch_manager, config.STEPS_PER_EPOCH)):
                startmodel.run_one_batch(x, y)

            # weights checking
            if not self._compare_weights(startmodel, endmodel):
                return False

        print("All tests passed")
        return True

    @staticmethod
    def _compare_weights(model1: IrisSimpleModel, model2: IrisSimpleModel):
        weights1 = model1.net.parameters()
        weights2 = model2.net.parameters()

        for x, y in zip(weights1, weights2):
            if not np.equal(x.data.numpy(), y.data.numpy()).all():
                print("Weights wrong!")
                return False
            print("Weights ok")
        return True

    @staticmethod
    def _get_hash_from_name(filepath: str):
        name = os.path.basename(filepath)
        return name.split(".")[0]

    @staticmethod
    def _find_file_with_ext(ext, dir):
        for file in os.listdir(dir):
            if file.split(".")[-1] == ext:
                return os.path.join(dir, file)

        raise Exception("In dir {} no file with ext {}".format(dir, ext))


    # def check_batch_hash(data, name):
    #     hash = _get_hash_from_name(name)
    #     return ... == hash


    # def load_batch(filename):
    #     with open(filename, "r") as f:
    #         return pickle.load(f)
