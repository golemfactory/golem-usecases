import os

from unittest import TestCase

import shutil

from impl import config
from impl.model import HonestModelRunner, DummyDishonestModelRunner, CyclicBufferDishonestModelRunner
from impl.verificator import Verificator


class TestVerificator(TestCase):
    def clean_up(self):
        for d in os.listdir(config.SHARED_PATH):
            shutil.rmtree(os.path.join(config.SHARED_PATH, d))

    def tearDown(self):
        self.clean_up()

    def test_verificate(self):
        probability_of_saving = 1
        number_of_epochs = 100

        self.clean_up()
        provider = HonestModelRunner(config.SHARED_PATH,
                                            probability_of_bb_saving=probability_of_saving,
                                            save_model_as_dict=config.SAVE_MODEL_AS_DICT,
                                            number_of_epochs=number_of_epochs)
        provider.run_full_training()
        verificator = Verificator(config.SHARED_PATH, probability_of_saving * number_of_epochs)
        self.assertTrue(verificator.verificate())

        self.clean_up()
        provider = DummyDishonestModelRunner(config.SHARED_PATH,
                                                    probability_of_cheating=0.5,
                                                    probability_of_bb_saving=probability_of_saving,
                                                    verbose=0,
                                                    save_model_as_dict=config.SAVE_MODEL_AS_DICT,
                                                    number_of_epochs=number_of_epochs)

        provider.run_full_training()
        verificator = Verificator(config.SHARED_PATH, probability_of_saving * number_of_epochs)
        self.assertFalse(verificator.verificate())
        self.clean_up()

        # NO_EPS = 0.0
        # LARGE_EPS = 0.1
        # SMALL_EPS = 0.000001
        # for eps in [NO_EPS, LARGE_EPS, SMALL_EPS]:
        #     self.clean_up()
        #     provider = CyclicBufferDishonestModelRunner(config.SHARED_PATH,
        #                                                        lenght_of_cb=20,
        #                                                        added_eps=eps,
        #                                                        probability_of_bb_saving=probability_of_saving,
        #                                                        verbose=0,
        #                                                        save_model_as_dict=config.SAVE_MODEL_AS_DICT,
        #                                                        number_of_epochs=number_of_epochs)
        #
        #     provider.run_full_training()
        #     verificator = Verificator(config.SHARED_PATH, probability_of_saving * number_of_epochs)
        #     self.assertFalse(verificator.verificate())