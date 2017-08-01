import os
import shutil
from unittest import TestCase
import math

from impl import config
from impl.model import HonestModelRunner, SkippingDishonestModelRunner
from impl.verificator import Verificator


class TestVerificator(TestCase):
    def clean_up(self):
        for d in os.listdir(config.SHARED_PATH):
            shutil.rmtree(os.path.join(config.SHARED_PATH, d))

    def tearDown(self):
        self.clean_up()

    def test_verificate(self):
        probability_of_saving = p = 0.01
        number_of_epochs = n = 1000

        # TODO change that!
        # do something to ensure that we always get the same number of samples
        # some maths
        # what we have here is binominal distribution with n, p as above
        # we want to have Exp(number_of_checkings) to stay ~constant
        # while n will be large, so we can approximate the Bin(n, p)
        # with Poiss(lambda=np).
        l = n * p
        # where expected value mu = l, variance = l
        # Then we want to get 95% confidence interval on value of X ~ Poiss(lambda)
        # Then we calculate alpha such that P(X > mu - alpha) < 0.05
        # which in the language of CDF is F(mu - alpha) < 0.05
        # and with the help of calculator we find that alpha ~ 6 (confidence interval 97%)
        confidence_interval = 6

        expected_number_of_files = (l, confidence_interval)
        self.clean_up()
        provider = HonestModelRunner(shared_path=config.SHARED_PATH,
                                     probability_of_bb_saving=probability_of_saving,
                                     save_model_as_dict=config.SAVE_MODEL_AS_DICT,
                                     number_of_epochs=number_of_epochs)
        provider.run_full_training()
        verificator = Verificator(config.SHARED_PATH, expected_number_of_files)
        self.assertTrue(verificator.verificate())

        self.clean_up()
        provider = SkippingDishonestModelRunner(
            probability_of_cheating=0.5,
            shared_path=config.SHARED_PATH,
            probability_of_bb_saving=probability_of_saving,
            save_model_as_dict=config.SAVE_MODEL_AS_DICT,
            number_of_epochs=number_of_epochs)

        provider.run_full_training()
        verificator = Verificator(config.SHARED_PATH, expected_number_of_files)
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
        #     verificator = Verificator(config.SHARED_PATH, expected_number_of_files)
        #     self.assertFalse(verificator.verificate())
